# Copyright 2018-2021 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from unittest.mock import MagicMock, patch

import pytest
import tornado.testing

from streamlit.errors import StreamlitAPIException
from streamlit.state.session_state import (
    GENERATED_WIDGET_KEY_PREFIX,
    get_session_state,
    LazySessionState,
    SessionState,
    Serialized,
    Value,
    WidgetMetadata,
    WStates,
)
from streamlit.proto.WidgetStates_pb2 import WidgetState as WidgetStateProto
from tests.server_test_case import ServerTestCase


identity = lambda x: x


class WStateTests(unittest.TestCase):
    def setUp(self):
        wstates = WStates()
        self.wstates = wstates

        widget_state = WidgetStateProto()
        widget_state.id = "widget_id_1"
        widget_state.int_value = 5
        wstates.set_from_proto(widget_state)
        wstates.set_widget_metadata(
            WidgetMetadata(
                id="widget_id_1",
                deserializer=lambda x: str(x),
                serializer=lambda x: int(x),
                value_type="int_value",
            )
        )

        wstates.set_from_value("widget_id_2", 5)
        wstates.set_widget_metadata(
            WidgetMetadata(
                id="widget_id_2",
                deserializer=identity,
                serializer=identity,
                value_type="int_value",
            )
        )

    def test_getitem_nonexistent(self):
        with pytest.raises(KeyError):
            self.wstates["nonexistent_widget_id"]

    def test_getitem_no_metadata(self):
        del self.wstates.widget_metadata["widget_id_1"]
        with pytest.raises(KeyError):
            self.wstates["widget_id_1"]

    def test_getitem_serialized(self):
        assert isinstance(self.wstates.states["widget_id_1"], Serialized)
        assert self.wstates["widget_id_1"] == "5"
        assert self.wstates.states["widget_id_1"] == Value("5")

    def test_getitem_value(self):
        assert self.wstates["widget_id_2"] == 5

    def test_len(self):
        assert len(self.wstates) == 2

    def test_iter(self):
        wstate_iter = iter(self.wstates)
        assert next(wstate_iter) == "widget_id_1"
        assert next(wstate_iter) == "widget_id_2"
        with pytest.raises(StopIteration):
            next(wstate_iter)

    def test_keys(self):
        assert self.wstates.keys() == {"widget_id_1", "widget_id_2"}

    def test_items(self):
        assert self.wstates.items() == {("widget_id_1", "5"), ("widget_id_2", 5)}

    def test_values(self):
        assert self.wstates.values() == {"5", 5}

    def test_cull_nonexistent(self):
        self.wstates.cull_nonexistent({"widget_id_1"})
        assert "widget_id_1" in self.wstates
        assert "widget_id_1" in self.wstates.widget_metadata
        assert "widget_id_2" not in self.wstates
        assert "widget_id_2" not in self.wstates.widget_metadata

    def test_get_serialized_nonexistent_id(self):
        assert self.wstates.get_serialized("nonexistent_id") is None

    def test_get_serialized_no_metadata(self):
        del self.wstates.widget_metadata["widget_id_2"]
        assert self.wstates.get_serialized("widget_id_2") is None

    def test_get_serialized_already_serialized(self):
        serialized = self.wstates.get_serialized("widget_id_2")
        assert serialized.id == "widget_id_2"
        assert serialized.int_value == 5

    def test_get_serialized(self):
        serialized = self.wstates.get_serialized("widget_id_1")
        assert serialized.id == "widget_id_1"
        assert serialized.int_value == 5

    @pytest.mark.skip()
    def test_get_serialized_array_value(self):
        # TODO(vincent)
        pass

    def test_as_widget_states(self):
        widget_states = self.wstates.as_widget_states()
        assert len(widget_states) == 2
        assert widget_states[0].id == "widget_id_1"
        assert widget_states[0].int_value == 5
        assert widget_states[1].id == "widget_id_2"
        assert widget_states[1].int_value == 5

    @pytest.mark.skip()
    def test_call_callback(self):
        raise NotImplemented

    @pytest.mark.skip()
    def test_clear_state(self):
        raise NotImplemented


@pytest.mark.skip()
class SessionStateTests(unittest.TestCase):
    def test_compact_state(self):
        raise NotImplemented

    def test_clear_state(self):
        raise NotImplemented

    def test_filtered_state(self):
        raise NotImplemented

    def is_new_state_value(self):
        raise NotImplemented

    def test_iter(self):
        raise NotImplemented

    def test_len(self):
        raise NotImplemented

    def test_str(self):
        raise NotImplemented

    def test_getitem(self):
        raise NotImplemented

    def test_setitem(self):
        raise NotImplemented

    def test_setitem_disallows_setting_created_widget(self):
        raise NotImplemented

    def test_delitem_errors(self):
        raise NotImplemented

    def test_getattr(self):
        raise NotImplemented

    def test_setattr(self):
        raise NotImplemented

    def test_delattr(self):
        raise NotImplemented

    def test_set_from_proto(self):
        raise NotImplemented

    def test_call_callbacks(self):
        raise NotImplemented

    def test_widget_changed(self):
        raise NotImplemented

    def test_reset_triggers(self):
        raise NotImplemented

    def test_cull_nonexistent(self):
        raise NotImplemented

    def set_metadata(self):
        raise NotImplemented

    def get_value_for_registration(self):
        raise NotImplemented

    def get_as_widget_states(self):
        raise NotImplemented


# LocalSourcesWatcher needs to be patched so that the side effects of the
# ReportSession instantiating one below are suppressed.
@patch("streamlit.report_session.LocalSourcesWatcher")
@patch("streamlit.report_thread.get_report_ctx")
class SessionStateHelperTests(ServerTestCase):
    @tornado.testing.gen_test
    def test_get_session_state(self, patched_get_report_ctx, _):
        yield self.start_server_loop()

        ws_client = yield self.ws_connect()
        session = list(self.server._session_info_by_id.values())[0].session

        mock_ctx = MagicMock()
        mock_ctx.session_id = session.id
        patched_get_report_ctx.return_value = mock_ctx

        assert isinstance(get_session_state(), SessionState)

    def test_get_session_state_error_if_no_ctx(self, patched_get_report_ctx, _):
        patched_get_report_ctx.return_value = None

        with pytest.raises(RuntimeError) as e:
            get_session_state()
        assert "We were unable to retrieve your Streamlit session." in str(e.value)

    @tornado.testing.gen_test
    def test_get_session_state_error_if_no_session(self, patched_get_report_ctx, _):
        yield self.start_server_loop()

        mock_ctx = MagicMock()
        mock_ctx.session_id = "nonexistent"
        patched_get_report_ctx.return_value = mock_ctx

        with pytest.raises(RuntimeError) as e:
            get_session_state()
        assert "We were unable to retrieve your Streamlit session." in str(e.value)


class LazySessionStateTests(unittest.TestCase):
    reserved_key = f"{GENERATED_WIDGET_KEY_PREFIX}-some_key"

    def setUp(self):
        self.lazy_session_state = LazySessionState()

    @pytest.mark.skip()
    def test_iter(self):
        raise NotImplemented

    @pytest.mark.skip()
    def test_len(self):
        raise NotImplemented

    @pytest.mark.skip()
    def test_getitem(self):
        raise NotImplemented

    def test_validate_key(self):
        with pytest.raises(StreamlitAPIException) as e:
            self.lazy_session_state._validate_key(self.reserved_key)
        assert "are reserved" in str(e.value)

    def test_getitem_reserved_key(self):
        with pytest.raises(StreamlitAPIException):
            self.lazy_session_state[self.reserved_key]

    @pytest.mark.skip()
    def test_setitem(self):
        raise NotImplemented

    def test_setitem_reserved_key(self):
        with pytest.raises(StreamlitAPIException):
            self.lazy_session_state[self.reserved_key] = "foo"

    @pytest.mark.skip()
    def test_delitem(self):
        raise NotImplemented

    def test_delitem_reserved_key(self):
        with pytest.raises(StreamlitAPIException):
            del self.lazy_session_state[self.reserved_key]

    @pytest.mark.skip()
    def test_getattr(self):
        raise NotImplemented

    def test_getattr_reserved_key(self):
        with pytest.raises(StreamlitAPIException):
            getattr(self.lazy_session_state, self.reserved_key)

    @pytest.mark.skip()
    def test_setattr(self):
        raise NotImplemented

    def test_setattr_reserved_key(self):
        with pytest.raises(StreamlitAPIException):
            setattr(self.lazy_session_state, self.reserved_key, "foo")

    @pytest.mark.skip()
    def test_delattr(self):
        raise NotImplemented

    def test_delattr_reserved_key(self):
        with pytest.raises(StreamlitAPIException):
            delattr(self.lazy_session_state, self.reserved_key)

    @pytest.mark.skip()
    def test_to_dict(self):
        raise NotImplemented
