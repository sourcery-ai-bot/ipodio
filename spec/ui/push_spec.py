# -*- coding: utf-8 -*-

from expects import expect
from mamba import describe, context, before, after

from spec.ui._ipod_helpers import *
from spec.ui._fixture import update_environment


with describe('ipodio push') as _:

    @before.all
    def setup_all():
        update_environment(_)
        bootstrap_ipod(_.mountpoint_path)

    @after.each
    def cleanup():
        empty_ipod(_.mountpoint_path)

    def should_return_an_error_with_no_files():
        execution = _.env.run(*_.cmd + ['push'], expect_error=True)

        expect(execution.stderr).to.have('Usage')

    def should_log_files_sent_to_the_ipod():
        execution = _.env.run(*_.cmd + ['push'] + _.song_paths)

        expect(execution.stdout.count('Sending')).to.be(len(_.songs))

    def should_find_files_within_a_given_directory():
        execution = _.env.run(*_.cmd + ['push', _.fixtures_path])

        expect(execution.stdout.count('ending')).to.be(len(_.songs))

    with context('with songs already in the iPod'):
        def should_refuse_to_duplicate_a_song():
            populate_ipod(_.mountpoint_path, _.songs)
            execution = _.env.run(*_.cmd + ['push'] + _.song_paths)

            expect(execution.stdout.count('Not sending')).to.be(len(_.songs))

    with context('with --force option'):
        def should_not_mind_duplicating_songs_already_in_the_ipod():
            number_of_added_songs = sum(1 for path in _.execution.files_created
                if 'iPod_Control/Music' in path and path.endswith('mp3'))

            expect(number_of_added_songs).to.be(2)

        def should_log_same_output_as_if_when_pushing_normally():
            expect(_.execution.stdout.count('Sending')).to.be(len(_.songs))

        @before.all
        def execution():
            _.execution = _.env.run(*_.cmd + ['--force', 'push'] + _.song_paths)

    with context('with --recursive option'):
        def should_find_files_within_a_directory_tree():
            execution = _.env.run(*_.cmd + ['push', '--recursive', _.fixtures_path])

            expect(execution.stdout.count('ending')).to.be(2 * len(_.songs))

        @before.each
        def setup_each():
            populate_ipod(_.mountpoint_path, _.songs)
