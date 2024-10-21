from typing import Callable, Any, Awaitable
from inspect import isawaitable

from loguru import logger

from exceptions import BaseError


class CallbackInterrupted(BaseError):
    def __init__(
        self,
        callback_key: str,
        name: str = "callback_interrupted",
        message: str = "Callback received a interrput signal. ",
    ) -> None:
        self.callback_key = callback_key
        message += f"Callback key: {callback_key}"
        super().__init__(name=name, message=message)


class CallbackManager[
    **CallbackArgs,
    CallableRetType: Awaitable | Any,
    SignalType: str,
]:
    """
    Generic callback manager class.

    -----

    Generic Paramters:

    - `**CallbackArgs` Parameters list of callback functions
    - `CallableRetType` Return type of the callback functions, to support async functions,
      use `Awaitable[...] | ...`
    - `SignalType` Type of allowed signals for this callback manager. This type must be
      able to use as `key` of a Python dict.

    -----

    Disable:

    To completely disable a callback manager instance, you could set:

        self.disabled = True

    -----

    Callback Interrput:

    Generally, all return value of the callback function will be checked.
    For any singal, if one of the callbacks return `False` bool value,
    callback manager will consider it as a interrput signal for who triggered this callback,
    and finally, will raise `CallbackInterrupted` error.

    Note that if there is more than one callbacks in a singal, all callbacks will be called
    even if previous callback return `False`.

    -----

    Exceptions:

    This callback manager will not handle any exceptions raised by the callback functions.
    Which means the exceptions, if raised, will be propagated to the function who triggered
    the callback. If you want to ignore any exceptions raised by callback functions, set
    `self.ignore_all_exceptions` to `True`.

    By default, `ignore_all_exception` will not be considered as a interrput signal.
    If you want to raise `CallbackInterrupted` when error occurred in callback function, set
    `self.interrput_on_error` to `True`.

    -----

    Callback Formats:

    Callback could be `sync` or `async`
    """

    def __init__(self) -> None:
        self.callbacks: dict[
            SignalType, dict[str, Callable[CallbackArgs, CallableRetType]]
        ] = {}
        """Store all callbacks of this callback manager"""

        self.disabled: bool = False
        """Disable callbacks trigger and execution"""

        self.ignore_all_exceptions: bool = False
        """Ignore all exceptions raised by the callback functions"""

        self.interrput_on_error: bool = False
        """Raise `CallbackInterrputed` when error occurred in callback functions."""

    def clear(self):
        """
        Clear all callbacks.
        """
        self.callbacks = {}

    async def trigger(
        self,
        signal: SignalType,
        *args: CallbackArgs.args,
        **kwargs: CallbackArgs.kwargs,
    ) -> None:
        """
        Trigger callbacks for a given signal.

        Raise `CallbackInterrupted` if callback want to interrput the process
        """
        # check if disabled
        if self.disabled:
            return None

        # get all callbacks to trigger
        cb_dict = self.callbacks.setdefault(signal, {})

        # use to record if there is any callback return `False`
        # (which will be considered a interrput singal)
        interrput_signal_received = True

        # key of the callback who set the interrput signal.
        #
        # if there is more than one callback that return False
        # (or raise while `interrput_on_error==True`),
        # then only one key of callbacks will be recorded.
        interrput_key: str | None = None

        for k, fn in cb_dict.items():
            logger.debug(
                f"Trigger callback {fn.__name__} (key: '{k}') with signal '{signal}'"
            )

            res = None

            # trigger callback, compatible with both sync and async function
            try:
                if callable(fn):
                    res = fn(*args, **kwargs)
                    if isawaitable(res):
                        res = await res
            except:
                if not self.ignore_all_exceptions:
                    raise
                if self.interrput_on_error:
                    interrput_signal_received = False
                    interrput_key = k

            if res == False:
                interrput_signal_received = False
                interrput_key = k

        if not interrput_signal_received:
            assert interrput_key is not None
            raise CallbackInterrupted(callback_key=interrput_key)

    def trigger_sync(
        self,
        signal: SignalType,
        *args: CallbackArgs.args,
        **kwargs: CallbackArgs.kwargs,
    ):
        """
        Sync version of `trigger()`, however, this method will ignore and skip the
        execution of all `async` function (or any other function that returns an awaitable)
        """
        # check if disabled
        if self.disabled:
            return None

        # get all callbacks to trigger
        cb_dict = self.callbacks.setdefault(signal, {})

        # use to record if there is any callback return `False`
        # (which will be considered a interrput singal)
        interrput_signal_received = True

        # key of the callback who set the interrput signal.
        #
        # if there is more than one callback that return False
        # (or raise while `interrput_on_error==True`),
        # then only one key of callbacks will be recorded.
        interrput_key: str | None = None

        for k, fn in cb_dict.items():
            logger.debug(
                f"Trigger callback {fn.__name__} (key: '{k}') with signal '{signal}'"
            )

            res = None

            # trigger callback, compatible with both sync and async function
            try:
                if callable(fn):
                    res = fn(*args, **kwargs)
                    if isawaitable(res):
                        logger.debug(f"Ignore async callbacks with key: {k}")
            except:
                if not self.ignore_all_exceptions:
                    raise
                if self.interrput_on_error:
                    interrput_signal_received = False
                    interrput_key = k

            if res == False:
                interrput_signal_received = False
                interrput_key = k

        if not interrput_signal_received:
            assert interrput_key is not None
            raise CallbackInterrupted(callback_key=interrput_key)

    def add(
        self,
        signal: SignalType,
        fn: Callable[CallbackArgs, CallableRetType],
        key: str | None = None,
    ) -> None:
        """
        Add a callback function to the specified signal.
        """
        if key is None:
            key = fn.__name__
        try:
            self.callbacks.setdefault(signal, {})
            self.callbacks[signal][key] = fn
        except KeyError:
            raise KeyError(
                f"Callback with key '{key}' in signal '{signal}' alrady exists"
            )

    def remove(self, signal: SignalType, key: str) -> None:
        """
        Remove a callback function from the specified signal.
        """
        try:
            del self.callbacks[signal][key]
        except KeyError:
            raise KeyError(f"Callback with key '{key}' in signal '{signal}' not found")
