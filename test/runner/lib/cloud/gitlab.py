from __future__ import absolute_import, print_function

import os

from lib.cloud import (
    CloudProvider,
    CloudEnvironment,
)

from lib.util import (
    find_executable,
    ApplicationError,
    display,
    SubprocessError,
)

from lib.docker_util import (
    docker_exec,
    docker_run,
    docker_rm,
    docker_inspect,
    docker_pull,
    docker_network_inspect,
    get_docker_container_id,
)


class GitLabCloudProvider(CloudProvider):
    """GitLab cloud provider plugin."""
    DOCKER_CONTAINER_NAME = 'gitlab-server'

    def __init__(self, args):
        """
        :type args: TestConfig
        """

        super(GitLabCloudProvider, self).__init__(args, config_extension='.yaml')

        self.image = 'gitlab/gitlab-ce:11.7.5-ce.0'
        self.container_name = ''


    def filter(self, targets, exclude):

        if os.path.isfile(self.config_static_path):
            return

        docker = find_executable('docker', required=False)

        if docker:
            return

        skip = 'cloud/%s/' % self.platform
        skipped = [target.name for target in targets if skip in target.aliases]

        if skipped:
            exclude.append(skip)
            display.warning('Excluding tests marked "%s"' % skip.rstrip('/'))

    def setup(self):
        super(GitLabCloudProvider, self).setup()

        if self._use_static_config():
            self._setup_static()
        else:
            self._setup_dynamic()


    def _setup_static(self):
        return

    def _setup_dynamic(self):
        self.container_name = self.DOCKER_CONTAINER_NAME

        results = docker_inspect(self.args, self.container_name)

        if results and not results[0]['State']['Running']:
            docker_rm(self.args, self.container_name)
            results = []

        if results:
            display.info('Using the existing GitLab container.', verbosity=1)
        else:
            display.info('Starting a new GitLab container.', verbosity=1)
            docker_pull(self.args, self.image)
            gitlab_container_params = ['-d', '--hostname gitlab.ansible.test', '--publish 80:80', '--publish 22:22',
            '--name ansible_gitlab_test_container', self.image]
            docker_run(self.args, self.image, gitlab_container_params)

        container_id = get_docker_container_id()

        if container_id:
            display.info('Running in container: %s' % container_id, verbosity=1)
            host = self._get_container_address()
            display.info('Found GitLab container address: %s' % host, verbosity=1)
        else:
            hsot = 'localhost'

        port = 80
        endpoint = 'http://%s:%s' % (host, port)

        self._wait_for_service(endpoint)







