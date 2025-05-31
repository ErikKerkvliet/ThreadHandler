import re
from typing import List, Optional, Dict

from Hcapital import Hcapital
from Update import Update
from ImgBB import ImgBB
from TurboImage import TurboImage
from AnimeSharing import AnimeSharing
from FillTemplate import FillTemplate

from config import USERNAMES, USERNAME_BOTH


class ThreadManager:
    def __init__(self, glv_instance=None):
        self.glv = glv_instance
        self.hcapital = Hcapital(self.glv)
        self.imgbb = ImgBB(self.glv)
        self.turbo_image = TurboImage(self.glv)
        self.sharing = AnimeSharing(self.glv)
        self.fill_template = FillTemplate(self.glv)
        self.update = Update(self.glv)

    def start(self, ids: Optional[List[int]] = None):
        """
        Main entry point for the ThreadManager. Manages thread creation, updating, and submission.

        :param ids: Optional list of thread IDs to process. If provided, these specific IDs will be processed;
                    otherwise, a default range of IDs will be generated.
        """
        self._initialize_session()

        # Determine the IDs to process and format them for logging
        if ids is not None:
            # Display the first ID followed by "+" if there are more than 10 IDs
            ids_str = f"{ids[0]}+" if len(ids) > 10 else ", ".join(map(str, ids))
            self.glv.log(f"Processing threads with IDs: {ids_str}")

        if self.glv.update:
            self._process_updates(ids)
        else:
            self._process_threads(ids)

        self._finalize_session()

    def _initialize_session(self):
        """Set up the initial state for the session."""
        self.glv.log(f"Session started at: {self.glv.get_time()}")
        self.glv.include_jquery(self.glv.driver)

        # if not self.glv.from_text:
        #     self.glv.driver.get('https://nl.imgbb.com/')
        #     time.sleep(5)

    def _process_updates(self, ids: List[int]):
        """Handle updating existing threads."""
        self.glv.reset()

        if self.glv.update_all:
            usernames = USERNAMES if self.glv.selected_username == USERNAME_BOTH else [self.glv.selected_username]
            for username in usernames:
                self.sharing.start(username)

        for entry_id in ids:
            self._update_single_thread(entry_id)

        self.glv.quit(True)

    def _update_single_thread(self, entry_id: int):
        """Update a single thread with the given ID."""
        self.glv.id = entry_id

        urls = self.glv.db.get_sharing_urls(entry_id)
        if len(urls) == 0:
            self.glv.create_thread = True
            self.glv.only_text = False
            self.glv.update = False
            self.glv.force = True

            self.start([entry_id])
            return

        data = self.update.update()

        if data:
            try:
                data['image_urls'] = self.turbo_image.upload(data['temp_images'])
            except Exception as e:
                print(f"Error uploading images to TurboImage: {e}")
                data['image_urls'] = self.imgbb.upload(data['temp_images'])

            self.sharing.update_thread(data, None)

        if self.glv.update_all:
            self.glv.write((entry_id + 1), 'fixId')
            self.glv.sleep(20)

    def _process_threads(self, ids: Optional[List[int]]):
        """Handle creation or processing of threads."""
        ids = self._generate_id_range() if ids is None else ids

        if self.glv.create_thread:
            for i, entry_id in enumerate(ids):
                self.glv.id = entry_id
                self._create_new_thread(ids, i)

                self._post_processing()

                self.glv.log('=========================================================')

                if self._should_stop_processing(entry_id):
                    break
        else:
            usernames = USERNAMES if self.glv.selected_username == USERNAME_BOTH else [self.glv.selected_username]
            for username in usernames:
                self.sharing.start(username)
                while True:
                    files = self.glv.get_folder_content(f'{self.glv.threads_folder}_{username}')
                    files = sorted(files)

                    if not files:
                        # Break the loop if no files are found
                        print("No files found. Exiting loop.")
                        break

                    for index, file in enumerate(files):
                        if index > 0 or ids == [0]:
                            # Sleep to throttle processing
                            self.glv.sleep(3600, 3800)

                        # Process the current file
                        self._process_existing_thread(file)

    def _generate_id_range(self) -> range:
        """Generate a range of IDs to process."""
        return range(self.glv.id, self.glv.id + 100)

    def _create_new_thread(self, ids: List[int], index: int):
        """Create a new thread and check for range."""
        self._setup_thread(isinstance(ids, range))
        if not self.glv.only_text:
            self.sharing.submit(self.glv.id)
            self.glv.log('---------------------------------------------------------')

            self.glv.sleep(3600, 3800)
        self._update_id(ids, index)
        self.glv.previous_error = False
        self.glv.reset()

    def _process_existing_thread(self, file):
        """Process an existing thread."""
        thread = self.glv.get_content_from_file(self.glv.selected_username, file)

        self.sharing.create_thread(thread['type'], thread)
        self._submit_and_cleanup(thread)

    def _setup_thread(self, is_range: bool):
        """Set up a new thread with the given ID."""
        if not self.glv.previous_error:
            self.glv.reset()

        if self.hcapital.start() == 'not possible':
            return

        self.glv.log(f'Starting with entry: {self.glv.id}')

        data = self._prepare_thread_data()

        usernames = USERNAMES if self.glv.selected_username == USERNAME_BOTH else [self.glv.selected_username]
        for username in usernames:
            self.glv.user = self.glv.get_sharing_account(username)
            thread = self.fill_template.create_thread(data)

            if self.glv.only_text:
                self.fill_template.store_thread(thread)
            else:
                self.sharing.start(username)
                self.sharing.create_thread(data, thread)

        # Handle range-specific logic for text-only mode
        if is_range and self.glv.only_text:
            self.glv.set_next_id()

        self.glv.log('---------------------------------------------------------')

    def _prepare_thread_data(self) -> Dict:
        """Prepare the data for a new thread."""
        data = self.hcapital.get_data()
        self.glv.fix_links(data)

        try:
            data['image_urls'] = self.turbo_image.upload(data['temp_images'])
        except Exception as e:
            print(f"Error uploading images to TurboImage: {e}")
            data['image_urls'] = self.imgbb.upload(data['temp_images'])

        return data

    def _submit_and_cleanup(self, thread: Dict):
        """Submit the thread and perform cleanup operations."""
        filename = thread['fileName']
        self.sharing.submit(re.findall(r"\d+", filename)[0])

        usernames = USERNAMES if self.glv.selected_username == USERNAME_BOTH else [self.glv.selected_username]
        for username in usernames:
            self.glv.remove_file(filename, username)

        if not self.glv.get_folder_content(f'{self.glv.threads_folder}_{self.glv.selected_username}'):
            self.glv.log(f"===============================================")
            self.glv.log('Finished successfully')
            self.glv.sleep(2)
            self.glv.quit(True)

    def _should_stop_processing(self, entry_id: int) -> bool:
        """Determine if thread processing should stop."""
        return self.glv.db.get_entry_by_id(entry_id) is None

    def _post_processing(self):
        """Perform post-processing steps after handling a thread."""
        self.hcapital.links = None
        self.glv.sleep(2)

    def _update_id(self, ids: List[int], index: int):
        """Update the current ID to the next one in the list."""
        try:
            self.glv.id = ids[index + 1]
        except IndexError:
            print('Error: No more IDs available')

    def _finalize_session(self):
        """Perform final cleanup and logging before ending the session."""
        self.glv.log('Finished successfully')
        self.glv.quit(True)
