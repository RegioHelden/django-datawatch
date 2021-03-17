# -*- coding: UTF-8 -*-


class BaseBackend(object):
    def enqueue(self, slug, run_async=True):
        raise NotImplementedError('enqueue not implemented')

    def refresh(self, slug, run_async=True):
        raise NotImplementedError('refresh not implemented')

    def run(self, slug, identifier, run_async=True, user_forced_refresh=False):
        raise NotImplementedError('run not implemented')
