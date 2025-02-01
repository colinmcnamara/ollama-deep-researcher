import unittest
from unittest.mock import patch
import responses
import requests
from mcp_client import MCPClient

class TestMCPClient(unittest.TestCase):
    def setUp(self):
        self.client = MCPClient("http://localhost:2024")

    @responses.activate
    def test_run_stateful(self):
        responses.add(
            responses.POST,
            "http://localhost:2024/threads/runs/wait",
            json={"run_id": "1234", "status": "success"},
            status=200,
        )

        run_details = self.client.run_stateful(
            assistant_id="my_assistant",
            input_data={"text": "Hello, world!"},
            config={"recursion_limit": 10},
        )

        self.assertEqual(run_details, {"run_id": "1234", "status": "success"})

    @responses.activate
    def test_run_stateless(self):
        responses.add(
            responses.POST,
            "http://localhost:2024/runs/wait",
            json={"output": "Hello, world!"},
            status=200,
        )

        run_output = self.client.run_stateless(
            assistant_id="my_assistant", input_data={"text": "Hello, world!"}
        )

        self.assertEqual(run_output, {"output": "Hello, world!"})

    @responses.activate
    def test_stream_run(self):
        responses.add(
            responses.POST,
            "http://localhost:2024/runs/stream",
            body="data: Hello\n\ndata: world!",
            status=200,
            stream=True,
        )

        response = self.client.stream_run(
            assistant_id="my_assistant", input_data={"text": "Hello, world!"}
        )

        # Verify that the response is a streaming response
        self.assertTrue(response.iter_lines())

    @responses.activate
    def test_get_run_status(self):
        responses.add(
            responses.GET,
            "http://localhost:2024/threads/1234/runs/5678",
            json={"run_id": "5678", "status": "success"},
            status=200,
        )

        run_details = self.client.get_run_status(thread_id="1234", run_id="5678")

        self.assertEqual(run_details, {"run_id": "5678", "status": "success"})

    @responses.activate
    def test_cancel_run(self):
        responses.add(
            responses.POST,
            "http://localhost:2024/threads/1234/runs/5678/cancel",
            status=200,
        )

        self.client.cancel_run(thread_id="1234", run_id="5678")
        self.assertTrue(len(responses.calls) == 1)

    @responses.activate
    def test_get_assistant_details(self):
        responses.add(
            responses.GET,
            "http://localhost:2024/assistants/my_assistant/schemas",
            json={
                "input_schema": {"type": "object", "properties": {"text": {"type": "string"}}},
                "output_schema": {"type": "object", "properties": {"response": {"type": "string"}}},
            },
            status=200,
        )

        assistant_details = self.client.get_assistant_details(assistant_id="my_assistant")

        self.assertEqual(
            assistant_details,
            {
                "input_schema": {"type": "object", "properties": {"text": {"type": "string"}}},
                "output_schema": {"type": "object", "properties": {"response": {"type": "string"}}},
            },
        )

    @responses.activate
    def test_get_thread_state(self):
        responses.add(
            responses.GET,
            "http://localhost:2024/threads/1234/state",
            json={"values": {"key": "value"}},
            status=200,
        )

        thread_state = self.client.get_thread_state(thread_id="1234")

        self.assertEqual(thread_state, {"values": {"key": "value"}})

    @responses.activate
    def test_update_thread_state(self):
        responses.add(
            responses.POST,
            "http://localhost:2024/threads/1234/state",
            json={"values": {"key": "new_value"}},
            status=200,
        )

        updated_state = self.client.update_thread_state(
            thread_id="1234", values={"key": "new_value"}
        )

        self.assertEqual(updated_state, {"values": {"key": "new_value"}})

    @responses.activate
    def test_put_item(self):
        responses.add(
            responses.PUT,
            "http://localhost:2024/store/items",
            status=204,
        )

        self.client.put_item(namespace=["my_namespace"], key="my_key", value={"data": "value"})
        self.assertTrue(len(responses.calls) == 1)

    @responses.activate
    def test_get_item(self):
        responses.add(
            responses.GET,
            "http://localhost:2024/store/items?namespace=my_namespace&key=my_key",
            json={"namespace": ["my_namespace"], "key": "my_key", "value": {"data": "value"}},
            status=200,
        )

        item = self.client.get_item(namespace=["my_namespace"], key="my_key")

        self.assertEqual(item, {"namespace": ["my_namespace"], "key": "my_key", "value": {"data": "value"}})

    @responses.activate
    def test_search_items(self):
        responses.add(
            responses.POST,
            "http://localhost:2024/store/items/search",
            json={
                "items": [
                    {"namespace": ["my_namespace"], "key": "my_key", "value": {"data": "value"}},
                    {"namespace": ["my_namespace"], "key": "other_key", "value": {"data": "other_value"}},
                ]
            },
            status=200,
        )

        search_results = self.client.search_items(namespace_prefix=["my_namespace"], filter={"data": "value"})

        self.assertEqual(
            search_results,
            {
                "items": [
                    {"namespace": ["my_namespace"], "key": "my_key", "value": {"data": "value"}},
                    {"namespace": ["my_namespace"], "key": "other_key", "value": {"data": "other_value"}},
                ]
            },
        )

    @responses.activate
    def test_api_error(self):
        responses.add(
            responses.POST,
            "http://localhost:2024/threads/runs/wait",
            json={"error": "Invalid input"},
            status=400,
        )

        with self.assertRaises(requests.exceptions.HTTPError):
            self.client.run_stateful(assistant_id="my_assistant", input_data={"text": "Hello, world!"})

if __name__ == "__main__":
    unittest.main()
