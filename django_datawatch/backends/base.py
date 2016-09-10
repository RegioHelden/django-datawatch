# -*- coding: UTF-8 -*-


class BaseBackend(object):
    def enqueue(self, slug, async=True):
        raise NotImplementedError('enqueue not implemented')

    def run(self, slug, identifier, async=True):
        raise NotImplementedError('run not implemented')
