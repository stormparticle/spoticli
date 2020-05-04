'''
SpotiCLI
Copyright 2020, Hugo A Lopez

released under the MIT license
'''

import argparse
import time

from tekore import Spotify, util
from cmd2 import Cmd, with_argparser
#from colorama import init, Fore, Back, Style

class SpotiCLI(Cmd):
    def __init__(self, token):
        super().__init__()

        app_name = 'SpotiCLI'
        version = '1.20.0504.dev'
        
        ###define app parameters
        self.app_info = f'\n{app_name} {version}'
        self.intro = self.app_info + '\n'
        self.prompt = 'spoticli ~$ '

        self.api_delay = 0.2

        self.sp_user = Spotify(token)

        #hide built-in cmd2 functions. this will leave them available for use but will be hidden from tab completion (and docs)
        self.hidden_commands.append('alias')
        self.hidden_commands.append('unalias')
        self.hidden_commands.append('set')
        self.hidden_commands.append('edit')
        self.hidden_commands.append('history')
        self.hidden_commands.append('load')
        self.hidden_commands.append('macro')
        self.hidden_commands.append('py')
        self.hidden_commands.append('pyscript')
        self.hidden_commands.append('shell')
        self.hidden_commands.append('shortcuts')
        self.hidden_commands.append('_relative_load')
        self.hidden_commands.append('run_pyscript')
        self.hidden_commands.append('run_script')
        self.debug = True

        ##define permissions scope...

    #### Misc / Util methods
    ##########################################
    
    '''
    convert milliseconds into human readable time stamp in format MM:SS 
    '''
    def ms_to_time(self, time_to_convert):

        #modulus to get seconds from ms timestamp
        seconds = (time_to_convert / 1000) % 60
        seconds = str(int(seconds))

        #modulus to get minutes from ms timestamp
        minutes = (time_to_convert / (1000 * 60)) % 60
        minutes = str(int(minutes))

        #if seconds is single digit, prefix with 0
        if(len(seconds) < 2):
            seconds = '0' + seconds

        #return formatted value
        return f'{minutes}:{seconds}'

    '''
    generate timestamp in format "length / duration" from song playback data  
    '''
    def generate_timestamp(self, song_data):
        pos_ms = self.ms_to_time(self.get_position(song_data))
        dur_ms = self.ms_to_time(self.get_duration(song_data))

        return f'{pos_ms} / {dur_ms}'

    #### accessor / mutators
    #### getter / setter, whatever
    #### these make the spotify api calls
    ##########################################
    
    def get_playback(self):
        return self.sp_user.playback()

    def get_current_playback(self):
        return self.sp_user.playback_currently_playing()

    ## accessors
    ############################

    # track specific
    ################

    def get_album(self, song_data):
        return song_data.item.album.name

    def get_artist(self, song_data):
        ### artists is an array as a song can have multiple artists
        ### if there is multiple artists, return name of _first_ artist in array (usually main artist)
        return song_data.item.artists[0].name

    def get_song(self, song_data):
        return song_data.item.name

    def get_song_id(self, song_data):
        return song_data.item.id

    def get_duration(self, song_data): 
        return song_data.item.duration_ms

    def get_is_playing(self, song_data):
        return song_data.is_playing

    def get_position(self, song_data): 
        return song_data.progress_ms

    # generic functions
    ################

    def force_device(self):
        current_dev = self.get_device()
        self.sp_user.playback_transfer(current_dev[0].asdict()['id'])

    def do_force(self, line):
        self.force_device()
    # generic accessors
    ################

    def get_device(self): 
        return self.sp_user.playback_devices()

    def get_history(self, last_songs): 
        return self.sp_user.playback_recently_played(last_songs)

    def get_repeat_state(self): 
        return self.get_playback().repeat_state

    def get_shuffle_state(self): 
        return self.get_playback().shuffle_state

    def get_volume(self): 
        return self.get_playback().device.volume_percent

    ## mutator
    ############################

    ## these methods add artificial delay after calling API
    ## this is needed to allow the API some time to 'catch-up' with our request
    ## needed as we'll usually send a 'get' request not long after and if we send too soon
    ## API might return wrong info

    def set_device(self): 
        self.pwarning('placeholder')
        time.sleep(self.api_delay)

    def set_position(self, new_time): 
        self.sp_user.playback_seek(new_time)
        time.sleep(self.api_delay)

    def set_repeat_state(self, new_repeat_state): 
        self.sp_user.playback_repeat(new_repeat_state)
        time.sleep(self.api_delay)

    def set_save(self, song_id):
        self.sp_user.saved_tracks_add(song_id)
        time.sleep(self.api_delay)

    def set_unsave(self, song_id):
        self.sp_user.saved_tracks_delete(song_id)
        time.sleep(self.api_delay)

    def set_shuffle_state(self, new_shuffle_state): 
        self.sp_user.playback_shuffle(new_shuffle_state)
        time.sleep(self.api_delay)

    def set_volume(self, new_volume): 
        self.sp_user.playback_volume(new_volume)
        time.sleep(self.api_delay)

    #### cmd2 native functions
    ##########################################
    
    #prints blank line
    #necessary to overload cmd2's default behavior (retry previous command)
    def emptyline(self):
        return

    #overloads default error message
    def default(self, line):
        self.perror('unrecognized command')

    #used to write an extra blank line between commands...just a formatting thing.
    def postcmd(self, line, stop):
        self.poutput('')
        return line

    #### Begin CMD2 commands below 
    ##########################################

    def do_about(self, line):
        '''
        show build information

        usage: 
            about
        '''
        self.poutput(self.app_info)

    def do_logout(self, line):
        '''
        logout current session and force login next program start

        usage:
            logout
        '''
        self.poutput('are you sure? type \'yes\' to proceed')
        is_user_sure = input()
        if (is_user_sure.lower() == 'yes'):
            try:
                #try to delete user token
                #self.pwarning('logged out')
                self.pwarning('placeholder, not implemented yet')
                pass
            except:
                self.perror('failed to logout')
                self.pwarning('unable to delete config files, please try manual removal')
                self.pwarning('can be found in your home config directory, .config/spoticli/')
                pass
        else:
            self.pwarning('not logged out')

    
    #### playback commands
    ##########################################

    ###
    ### [Playing - 0:05 / 4:24] Make Me Wanna Die by The Pretty Reckless on Make Me Wanna Die
    ### [Stopped - 0:05 / 4:24] Make Me Wanna Die by The Pretty Reckless on Make Me Wanna Die
    def do_current(self, line):
        '''
        show currently playing track

        usage:
            current
        '''
        #now_playing = f'[{playing_state} - {timestamp}] {song_name} by {artist_name} on {album_name}'
        song_data = self.get_current_playback()
        song_name = self.get_song(song_data)
        song_album = self.get_album(song_data)
        song_artist = self.get_artist(song_data)
        
        song_playing = self.get_is_playing(song_data)

        if(song_playing == True):
            song_playing = 'Playing'
        else:
            song_playing = 'Stopped'

        time_stamp = self.generate_timestamp(song_data)
        
        now_playing = f'[{song_playing} - {time_stamp}] {song_name} by {song_artist} on {song_album}'
        self.poutput(now_playing)

    def play_next(self, args):
        self.sp_user.playback_next()
        self.poutput('playing next')

    def play_previous(self, args):
        self.sp_user.playback_previous()
        self.poutput('playing previous')

    play_parser = argparse.ArgumentParser(prog='play', add_help=False)
    play_subparsers = play_parser.add_subparsers(title='playback options')

    parser_play_next = play_subparsers.add_parser('next', help='next track', add_help=False)
    parser_play_next.set_defaults(func=play_next)

    parser_play_previous = play_subparsers.add_parser('previous', help='previos track', add_help=False)
    parser_play_previous.set_defaults(func=play_previous)

    play_subcommands = ['next', 'previous']

    @with_argparser(play_parser)
    def do_play(self, line):
        '''
        start or resume playback, or play next/previous song

        usage:
            play [next|previous]
        '''

        # Call whatever sub-command function was selected
        try:
            line.func(self, line)
        #if none specified do default action (start playback)
        except AttributeError:
            try:
                self.sp_user.playback_resume()
            except:
                pass
                
    def do_pause(self, line):
        '''
        pause playback

        usage:
            pause
        '''
        try:
            self.sp_user.playback_pause()
        except:
            pass

    def do_seek(self, line):
        '''
        seek to specific time in a track
        you can also specify a step increase by prefixing time with +/-
        time should be in seconds or as a timestamp value, ie. 1:41

        usage:
            seek [+/-][time]
        '''

        ## no value specified; exit
        if(not line):
            self.do_help('seek')
            return

        try:
            new_pos = 1000 * int(line)
        #non-numerical value specified; exit
        except ValueError:
            self.perror('invalid time')
            return

        song_data = self.get_current_playback()
        song_pos = self.get_position(song_data)
        song_dur = self.get_duration(song_data)

        #if new time is larger than song duration, quit
        if((new_pos > song_dur) or (new_pos < (song_dur * -1))):
            self.perror('invalid time')
            return

        if(line[0] == '+' or line[0] == '-'):
            song_pos = song_pos + new_pos
            self.set_position(song_pos)
        else:
            self.set_position(new_pos)

    #### playback properties
    ##########################################

    def do_volume(self, line):
        '''
        set volume to specified level, range 0-100
        specify a step increase by prefixing value with +/-, otherwise it defaults to 10% step
        
        usage: 
            volume [+/-][value]
        '''

        current_vol = self.get_volume()

        if(line):
            try:
                new_vol = int(line)
                if(line[0] == '+' or line[0] == '-'):
                    new_vol = new_vol + current_vol
            except ValueError:
                if(line[0] == '+'):
                    new_vol = current_vol + 10
                elif(line[0] == '-'):
                    new_vol = current_vol - 10
                else:
                    self.perror('invalid volume')
                    return

            if new_vol > 100:
                new_vol = 100
            elif new_vol < 0:
                new_vol = 0
            self.set_volume(new_vol)
        self.poutput(f'current volume: {self.get_volume()}')


    def do_endpoint(self, line):
        '''
        transfer playback between valid spotify connect endpoints

        usage:
            endpoint
        '''
        self.poutput(self.get_device())
    
    def repeat_enable(self, args):
        self.set_repeat_state('context')
        self.do_repeat('')

    def repeat_track(self, args):
        self.set_repeat_state('track')
        self.do_repeat('')

    def repeat_disable(self, args):
        self.set_repeat_state('off')
        self.do_repeat('')

    repeat_parser = argparse.ArgumentParser(prog='repeat', add_help=False)
    repeat_subparsers = repeat_parser.add_subparsers(title='repeat states')

    parser_repeat_track = repeat_subparsers.add_parser('track', help='repeat track', add_help=False)
    parser_repeat_track.set_defaults(func=repeat_track)

    parser_repeat_enable = repeat_subparsers.add_parser('enable', help='enable repeat', add_help=False)
    parser_repeat_enable.set_defaults(func=repeat_enable)

    parser_repeat_disable = repeat_subparsers.add_parser('disable', help='disable repeat', add_help=False)
    parser_repeat_disable.set_defaults(func=repeat_disable)

    repeat_subcommands = ['track', 'enable','disable']

    @with_argparser(repeat_parser)
    def do_repeat(self, line):
        '''
        show or modify repeat state

        usage: 
            repeat [enable|disable|track]
        '''

        # Call whatever sub-command function was selected
        try:
            line.func(self, line)
        except AttributeError:
            current_repeat = self.get_repeat_state().value

            ### valid states: 
            ### track - repeat enabled for track
            ### enabled - repeat enabled for playlist/album
            ### disabled - repeat disabled

            if(current_repeat == 'context'):
                self.poutput('repeat is enabled')
            elif(current_repeat == 'off'):
                self.poutput('repeat is disabled')
            elif(current_repeat == 'track'):
                self.poutput('repeating track')

    def shuffle_enable(self, args):
        self.set_shuffle_state(True)
        self.do_shuffle('')

    def shuffle_disable(self, args):
        self.set_shuffle_state(False)
        self.do_shuffle('')

    shuffle_parser = argparse.ArgumentParser(prog='shuffle', add_help=False)
    shuffle_subparsers = shuffle_parser.add_subparsers(title='shuffle states')

    # create the parser for the "foo" sub-command
    parser_shuffle_enable = shuffle_subparsers.add_parser('enable', help='enable shuffle', add_help=False)
    parser_shuffle_enable.set_defaults(func=shuffle_enable)

    # create the parser for the "foo" sub-command
    parser_shuffle_disable = shuffle_subparsers.add_parser('disable', help='disable shuffle', add_help=False)
    parser_shuffle_disable.set_defaults(func=shuffle_disable)

    shuffle_subcommands = ['enable','disable']

    @with_argparser(shuffle_parser)
    def do_shuffle(self, line):
        '''
        show or modify shuffle state

        usage:
            shuffle [enable|disable]
        '''
        ### valid states: 
        ### enabled - shuffle enabled
        ### disabled - shuffle disabled

        #if line is empty, print shuffle state 
        try:
            line.func(self, line)
        except AttributeError:
            if(self.get_shuffle_state()):
                self.poutput('shuffle is enabled')
            else:
                self.poutput('shuffle is disabled')

    #### playlist modification
    ##########################################

    def do_list(self, line):
        '''
        display user playlists

        usage:
            lists
        '''
        self.pwarning('placeholder')

    def do_previous(self, line):
        '''
        show last 10 songs (or more)

        usage:
            previous [integer]
        '''
        for index, prev_song in enumerate(self.get_history(10).items):
            self.poutput(f'{index + 1}: {prev_song.track.name}')
    
    def do_queue(self, line):
        '''
        show and modify queue

        usage:
            queue
        '''
        self.poutput('not implemented. pending expansion of spotify api')

    def do_save(self, line):
        '''
        add currently playing track to liked songs
        
        usage:
            save
        '''
        song_data  = self.get_playback()

        song_id = self.get_song_id(song_data)
        song_name = self.get_song(song_data)

        self.set_save([song_id])
        self.poutput(f'<3 - saved song - {song_name}')
    
    def do_unsave(self, line):
        '''remove currently playing track from liked songs
        
        usage:
            unsave
        '''
        song_data  = self.get_playback()

        song_id = self.get_song_id(song_data)
        song_name = self.get_song(song_data)

        self.set_unsave([song_id])
        self.poutput(f'</3 - removed song - {song_name}')

    def do_search(self, line):
        '''
        search by track, artist or album
        
        usage:
            search [filter] [-c amount] query

        filters:
            -a, --artist
            -b, --album
            -p, --playlist
            -t, --track

        examples: 
            search -t seven nation army
            search -a eminem
            search --playlist -c 3 cool songs
        '''

        if(not line):
            self.pwarning('no query detected')
            self.do_help('search')
            return

        result_limit = 5
        result_type = ('album','artist','track')

        ### turn into a list so we can check first flag (if any)
        search_string = line.split(' ')

        if ('-a' in search_string[0]):
            result_type = ('artist',)
            search_string.remove('-a')
            result_limit = 10
        elif ('-b' in search_string[0]):
            result_type = ('album',)
            search_string.remove('-b')
            result_limit = 10
        elif ('-p' in search_string[0]):
            result_type = ('playlist',)
            search_string.remove('-p')
            result_limit = 10
        elif ('-t' in search_string[0]):
            result_type = ('track',)
            search_string.remove('-t')
            result_limit = 10

        #if no flags detected search first 5 results of all 4 categories
        #else it'll do search for specific categore and return first 10

        ##once we finish checking flags turn back into a string and pass along to search call
        search_string = ' '.join(search_string)

        search_results = self.sp_user.search(types=result_type, limit=result_limit, query=search_string)
        #print(search_results)
        for thing, index in enumerate(search_results):
            for item in search_results[thing].items:
                media_type = item.type

                if(media_type == 'track'):
                    self.poutput(f'{media_type} - {item.name} by {item.artists[0].name} on {item.album.name}')
                if(media_type == 'artist'):
                    self.poutput(f'{media_type} - {item.name}')
                if(media_type == 'album'):
                    self.poutput(f'{media_type} - {item.name} by {item.artists[0].name}')
                if(media_type == 'playlist'):
                    self.poutput(f'{media_type} - {item.name}')

        #for index, item in enumerate(search_results):
            #print(f'{index} : {self.get_song(item[index].items[0].name)}')