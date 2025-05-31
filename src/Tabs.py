from config import USERNAME_2, USERNAME_3


class Tabs:
    def __init__(self, glv):
        self.glv = glv
        self.template = ''
        self.link_set = []

    def create_links(self, link_sets):
        if not link_sets:
            return ''

        self.link_set = link_sets
        self.template = ''

        if self.glv.user['username'] == USERNAME_2 or self.glv.user['username'] == USERNAME_3:
            for host, links in link_sets.items():
                self.only_links(host, links)
            return self.template

        host_key = list(link_sets.keys())[0]
        if len(link_sets[host_key].keys()) == 1:
            key = list(link_sets[host_key].keys())[0]
            if len(link_sets[host_key][key]) == 1:
                return self.create_host_links(link_sets, key)

        # Create tabbed links
        self.template += '[COLOR=transparent][FLEFT]xx[/FLEFT][FLEFT]xx[/FLEFT][FLEFT]xx[/FLEFT][FLEFT]xx[/FLEFT][/COLOR][TABS width=500]\n'
        for host, links in link_sets.items():
            self.create_tab(host, links)
        self.template += '[/TABS]'

        return self.template

    def create_tab(self, host, link_set):
        if len(link_set[list(link_set.keys())[0]]) < 1:
            return

        self.template += f'[SLIDE_HEADER][B]{host.capitalize()}[/B][/SLIDE_HEADER]\n'
        self.template += '[SLIDE]'

        old_comment = ''
        for comment in link_set.keys():
            if comment != old_comment and comment != '#':
                old_comment = comment
                self.template += f'\n{comment}\n'
            self.create_slide_content(link_set[comment])
        self.template += '[/SLIDE]'

    def create_slide_content(self, links):
        for link in links:
            renamed = self.rename_link(link)
            self.template += f'[URL={link}]{renamed}[/URL]\n'

    @staticmethod
    def create_host_links(link_sets, key):
        templates = []
        for host in link_sets.keys():
            template = f'[URL=#link#][B]#host#[/B][/URL]'
            template = template.replace('#host#', host.capitalize())
            if len(link_sets[host][key]) == 0:
                continue
            template = template.replace('#link#', link_sets[host][key][0])
            templates.append(template)
        return ' | '.join(templates)

    def rename_link(self, link):
        renamed = link.replace('rapidgator.net', 'rg.to')
        url_split = renamed.split('/')
        split = url_split[-1].split('.')

        if self.glv.user['username'] == USERNAME_2:
            name = self.glv.romanji_title.split(' ')[0]
            return f'{"/".join(url_split[:-1])}/{name}.' + split[1]

        if len(split) > 1:
            entry_id = self.get_full_id(self.glv.id)
            return f'{"/".join(url_split[:-1])}/E{entry_id}.' + split[1]
        return renamed

    def only_links(self, host, link_set):
        if len(link_set[list(link_set.keys())[0]]) < 1:
            return

        self.template += f'[B]{host.capitalize()}[/B]\n'

        old_comment = ''
        for comment in link_set.keys():
            if comment != old_comment and comment != '#':
                old_comment = comment
                self.template += f'\n{comment}\n'
            self.create_slide_content(link_set[comment])

    def get_full_id(self, entry_id):
        if len(f'{entry_id}') < 4:
            entry_id = f'0{entry_id}'
            self.get_full_id(entry_id)
        return entry_id
