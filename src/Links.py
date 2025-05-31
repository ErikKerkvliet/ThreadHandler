class Links:

    def __init__(self, glv):
        self.glv = glv
        self.template = ''
        self.host_label = ''
        self.templates = []
        self.links = []

    def create_template(self, link_groups):
        self.host_label = ' | '.join(link_groups.keys())
        for i, key in enumerate(link_groups.keys()):
            if i != 0:
                self.template += ' | '
            self.template += f'#{key}#'

        hosts = link_groups.keys()
        set_keys = []
        for host in hosts:
            set_keys = list(link_groups[host].keys())
            break

        for set_key in set_keys:
            if set_key == '#' and len(set_keys) > 1:
                continue
            self.links = []
            for i, host in enumerate(hosts):
                if i == 0:
                    if set_key != '#':
                        self.templates.append(f'\n[H4][CENTER][SIZE=3]{set_key}[/SIZE][/CENTER][/H4]')
                    if len(link_groups[host][set_key]) > 1:
                        self.templates.append(self.host_label)
                self.create_set(link_groups[host][set_key], host, i == 0)

            self.templates = self.templates + self.links

        if self.templates[0] == '#' and len(self.templates[0]['#']) == 2:
            self.templates.remove('#')

        template = '\n'.join(self.templates)
        self.reset()

        return template

    def create_set(self, links, host, first=False):
        single = True if len(links) == 1 else False
        for i, link in enumerate(links):
            if first:
                self.links.append(self.template)

            label = host.capitalize() if single else f'Part {i + 1}'
            self.links[i] = self.links[i].replace(f'#{host}#', f'[URL={link}][COLOR=#00141c][B]{label}[/B][/COLOR][/URL]')

    def reset(self):
        self.template = ''
        self.host_label = ''
        self.templates = []
        self.links = []
