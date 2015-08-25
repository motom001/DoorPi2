# -*- coding: utf-8 -*-

import threading
import time # used by: fire_event_synchron
from inspect import isfunction, ismethod # used by: register_action
import string, random # used by event_id

from main import DOORPI
logger = DOORPI.register_module(__name__, return_new_logger = True)

from resources.event_handler.docs import DOCUMENTATION as EVENT_HANDLER_DOCUMENTATION
from resources.event_handler.classes import SingleAction, EventHistoryHandler
from resources.event_handler.time_tick import TimeTicker

class ControlPulseAction(SingleAction): pass

class EventHandler:

    _conf = []
    _history = None

    _sources = [] # Auflistung Sources
    _events = {} # Zuordnung Event zu Sources (1 : n)
    _actions = {} # Zuordnung Event zu Actions (1: n)

    _destroy = False

    _time_ticker = TimeTicker()
    _last_heart_beat = 1

    @property
    def get_action_class(self): return SingleAction

    @property
    def pulse(self): return 1 / self._last_heart_beat

    @property
    def random_id(self): return self.generate_id()

    @staticmethod
    def generate_id(size = 6, chars = string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def __init__(self):
        DOORPI.register_module(__name__, self.start, self.stop, False)

    def start(self):
        logger.debug("start EventHandler")
        self._conf = DOORPI.config.get_modul_config(__name__)
        self._history = EventHistoryHandler().start(
            db_type =           DOORPI.config('/resources/event_handler/event_log/typ', 'sqlite'),
            connection_string = DOORPI.config('/resources/event_handler/event_log/connection_string', '!BASE_PATH!/conf/event_log.db'),
        )
        self._time_ticker = TimeTicker().start()
        DOORPI.events.register_action('OnTimeSecond', ControlPulseAction(self.control_pulse))
        return self

    def log_realtime_event(self):
        logger.debug('realtime event fired')

    def control_pulse(self):
        if self._destroy: return
        if DOORPI.CONST.HEART_BEAT_LEVEL_CRITICAL and self.pulse  < DOORPI.CONST.HEART_BEAT_LEVEL_CRITICAL: logger.critical('DoorPi pulse is %s', self.pulse)
        elif DOORPI.CONST.HEART_BEAT_LEVEL_ERROR and self.pulse   < DOORPI.CONST.HEART_BEAT_LEVEL_ERROR:    logger.error('DoorPi pulse is %s', self.pulse)
        elif DOORPI.CONST.HEART_BEAT_LEVEL_WARNING and self.pulse < DOORPI.CONST.HEART_BEAT_LEVEL_WARNING:  logger.warning('DoorPi pulse is %s', self.pulse)
        elif DOORPI.CONST.HEART_BEAT_LEVEL_INFO and self.pulse    < DOORPI.CONST.HEART_BEAT_LEVEL_INFO:     logger.info('DoorPi pulse is %s', self.pulse)
        elif DOORPI.CONST.HEART_BEAT_LEVEL_DEBUG and self.pulse   < DOORPI.CONST.HEART_BEAT_LEVEL_DEBUG:    logger.debug('DoorPi pulse is %s', self.pulse)

    def stop(self):
        logger.info('stop event handler')
        self._destroy = True
        self._time_ticker.stop()
        self._history.stop()
        return self

    def heart_beat(self):
        start = time.time()
        self._time_ticker.do_tick_tack(time_for_this_tick = self._last_heart_beat * 0.5 + DOORPI.CONST.HEART_BEAT_BASE_VALUE)
        self._last_heart_beat = time.time() - start
        return not self._destroy

    def log_for_event(self, event_name):
        return 'OnTime' not in event_name

    def register_source(self, event_source):
        if event_source not in self._sources:
            self._sources.append(event_source)
            logger.debug("event_source %s was added", event_source)
        return True

    def register_event(self, event_name, event_source):
        log = self.log_for_event(event_name)
        if log: logger.debug("register Event %s from %s ", event_name, event_source)
        self.register_source(event_source)
        if event_name not in self._events:
            self._events[event_name] = [event_source]
            if log: logger.debug("added event_name %s and registered source %s", event_name, event_source)
        elif event_source not in self._events[event_name]:
            self._events[event_name].append(event_source)
            if log: logger.debug("added event_source %s to existing event %s", event_source, event_name)
        else:
            if log: logger.debug("nothing to do - event %s from source %s is already known", event_name, event_source)

    def fire_event(self, event_name, event_source, syncron = False, kwargs = None):
        if syncron is False: return self.fire_event_asynchron(event_name, event_source, kwargs)
        else: return self.fire_event_synchron(event_name, event_source, kwargs)

    def fire_event_asynchron(self, event_name, event_source, kwargs = None):
        log = self.log_for_event(event_name)
        if self._destroy and not silent: return False
        if log: logger.debug("fire Event %s from %s asyncron", event_name, event_source)
        return threading.Thread(
            target = self.fire_event_synchron,
            args = (event_name, event_source, kwargs),
            name = "%s from %s" % (event_name, event_source)
        ).start()

    def fire_event_synchron(self, event_name, event_source, kwargs = None):
        log = self.log_for_event(event_name)
        if self._destroy and log: return False

        event_fire_id = self.random_id
        start_time = time.time()

        if event_source not in self._sources:
            logger.warning('[%s] source %s unknown - skip fire_event %s', event_fire_id, event_source, event_name)
            return "source unknown"
        if event_name not in self._events:
            logger.warning('[%s] event %s unknown - skip fire_event %s from %s', event_fire_id, event_name, event_name, event_source)
            return "event unknown"
        if event_source not in self._events[event_name]:
            logger.warning('[%s] source %s unknown for this event - skip fire_event %s from %s', event_fire_id, event_name, event_name, event_source)
            return "source unknown for this event"
        if event_name not in self._actions:
            if log: logger.debug('[%s] no actions for event %s - skip fire_event %s from %s', event_fire_id, event_name, event_name, event_source)
            return "no actions for this event"

        if kwargs is None: kwargs = {}
        # TODO: Hole auch die default Parameter aus dem doc
        kwargs.update({
            'last_fired': str(start_time),
            'last_fired_from': event_source,
            'event_fire_id': event_fire_id
        })

        #self.__additional_informations[event_name] = kwargs
        #if 'last_finished' not in self.__additional_informations[event_name]:
        #    self.__additional_informations[event_name]['last_finished'] = None
        #
        #if 'last_duration' not in self.__additional_informations[event_name]:
        #    self.__additional_informations[event_name]['last_duration'] = None

        if log: logger.debug("[%s] fire for event %s this actions %s ", event_fire_id, event_name, self._actions[event_name])
        for action in self._actions[event_name]:
            if log: logger.debug("[%s] try to fire action %s", event_fire_id, action)
            try:
                result = action.run(not log)
                #if log: self.db.insert_action_log(event_fire_id, action.name, start_time, result)
                # TODO: Besser aufräumen !
                if action.single_fire_action is True: del action
            except SystemExit as exp:
                logger.info('[%s] Detected SystemExit and shutdown DoorPi (Message: %s)', event_fire_id, exp)
                DOORPI.stop()
            except KeyboardInterrupt as exp:
                logger.info("[%s] Detected KeyboardInterrupt and shutdown DoorPi (Message: %s)", event_fire_id, exp)
                DOORPI.stop()
            except:
                logger.exception("[%s] error while fire action %s for event_name %s", event_fire_id, action, event_name)
        if log: logger.debug("[%s] finished fire_event for event_name %s", event_fire_id, event_name)
        #self.__additional_informations[event_name]['last_finished'] = str(time.time())
        #self.__additional_informations[event_name]['last_duration'] = str(time.time() - start_time)
        return True

    def unregister_event(self, event_name, event_source, delete_source_when_empty = True):
        try:
            logger.trace("unregister Event %s from %s ", event_name, event_source)
            if event_name not in self.__Events: return "event unknown"
            if event_source not in self.__Events[event_name]: return "source not know for this event"
            self.__Events[event_name].remove(event_source)
            if len(self.__Events[event_name]) is 0:
                del self.__Events[event_name]
                logger.debug("no more sources for event %s - remove event too", event_name)
            if delete_source_when_empty: self.unregister_source(event_source)
            logger.debug("event_source %s was removed for event %s", event_source, event_name)
            return True
        except Exception as exp:
            logger.error('failed to unregister event %s with error message %s', event_name, exp)
            return False

    def unregister_source(self, event_source, force_unregister = False):
        try:
            logger.debug("unregister Eventsource %s and force_unregister is %s", event_source, force_unregister)
            if event_source not in self.__Sources: return "event_source %s unknown" % (event_source)
            for event_name in self.__Events.keys():
                if event_source in self.__Events[event_name] and force_unregister:
                    self.unregister_event(event_name, event_source, False)
                elif event_source in self.__Events[event_name] and not force_unregister:
                    return "couldn't unregister event_source %s because it is used for event %s" % (event_source, event_name)
            if event_source in self.__Sources:
                # sollte nicht nötig sein, da es entfernt wird, wenn das letzte Event dafür gelöscht wird
                self.__Sources.remove(event_source)
            logger.debug("event_source %s was removed", event_source)
            return True
        except Exception as exp:
            logger.exception('failed to unregister source %s with error message %s', event_source, exp)
            return False

    def register_action(self, event_name, action_object, *args, **kwargs):
        if ismethod(action_object) and callable(action_object):
            action_object = SingleAction(action_object, *args, **kwargs)
        elif isfunction(action_object) and callable(action_object):
            action_object = SingleAction(action_object, *args, **kwargs)
        elif not isinstance(action_object, SingleAction):
            action_object = SingleAction.from_string(action_object)

        if action_object is None:
            logger.error('action_object is None')
            return False

        if 'single_fire_action' in kwargs.keys() and kwargs['single_fire_action'] is True:
            action_object.single_fire_action = True
            del kwargs['single_fire_action']

        if event_name in self._actions:
            self._actions[event_name].append(action_object)
            logger.debug("action %s was added to event %s", action_object, event_name)
        else:
            self._actions[event_name] = [action_object]
            logger.debug("action %s was added to new evententry %s", action_object, event_name)

        return action_object

    __call__ = fire_event_asynchron


