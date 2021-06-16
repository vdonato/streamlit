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

from streamlit.errors import StreamlitAPIException
from streamlit.proto.ForwardMsg_pb2 import ForwardMsg
from streamlit.report_thread import ReportContext
from streamlit.state.session_state import SessionState
from streamlit.uploaded_file_manager import UploadedFileManager


class ReportContextTest(unittest.TestCase):
    def test_set_page_config_immutable(self):
        """st.set_page_config must be called at most once"""

        fake_enqueue = lambda msg: None
        ctx = ReportContext(
            "TestSessionID",
            fake_enqueue,
            "",
            SessionState(),
            UploadedFileManager(),
        )

        msg = ForwardMsg()
        msg.page_config_changed.title = "foo"

        ctx.enqueue(msg)
        with self.assertRaises(StreamlitAPIException):
            ctx.enqueue(msg)

    def test_set_page_config_first(self):
        """st.set_page_config must be called before other st commands"""

        fake_enqueue = lambda msg: None
        ctx = ReportContext(
            "TestSessionID",
            fake_enqueue,
            "",
            SessionState(),
            UploadedFileManager(),
        )

        markdown_msg = ForwardMsg()
        markdown_msg.delta.new_element.markdown.body = "foo"

        msg = ForwardMsg()
        msg.page_config_changed.title = "foo"

        ctx.enqueue(markdown_msg)
        with self.assertRaises(StreamlitAPIException):
            ctx.enqueue(msg)

    def test_set_page_config_reset(self):
        """st.set_page_config should be allowed after a rerun"""

        fake_enqueue = lambda msg: None
        ctx = ReportContext(
            "TestSessionID",
            fake_enqueue,
            "",
            SessionState(),
            UploadedFileManager(),
        )

        msg = ForwardMsg()
        msg.page_config_changed.title = "foo"

        ctx.enqueue(msg)
        ctx.reset()
        try:
            ctx.enqueue(msg)
        except StreamlitAPIException:
            self.fail("set_page_config should have succeeded after reset!")
