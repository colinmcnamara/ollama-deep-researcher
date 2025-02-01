import requests
from typing import Optional, Union, Dict, Any

class MCPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

    def run_stateful(
        self,
        assistant_id: str,
        input_data: Optional[Union[str, Dict, list]] = None,
        config: Optional[Dict] = None,
        checkpoint: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """
        Execute a stateful run on an existing thread.

        Args:
            assistant_id (str): The ID of the assistant or graph name to run.
            input_data (Optional[Union[str, Dict, list]]): The input data for the run.
            config (Optional[Dict]): The configuration for the assistant.
            checkpoint (Optional[Dict]): The checkpoint to resume from.
            metadata (Optional[Dict]): Metadata to assign to the run.
            **kwargs: Additional parameters for the run.

        Returns:
            Dict: The details of the created run.
        """
        payload = {
            "assistant_id": assistant_id,
            "input": input_data,
            "config": config,
            "checkpoint": checkpoint,
            "metadata": metadata,
        }
        payload.update(kwargs)

        url = f"{self.base_url}/threads/runs/wait"
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def get_assistant_schema(self, assistant_id: str) -> Dict:
        """
        Fetch the input schema of an assistant.
        
        Args:
            assistant_id (str): The ID of the assistant.
        
        Returns:
            Dict: The input schema of the assistant.
        """
        details = self.get_assistant_details(assistant_id)
        return details.get("input_schema", {})

    def run_stateless(
        self,
        assistant_id: str,
        input_data: Optional[Union[str, Dict, list]] = None,
        config: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """
        Execute a stateless run.
        
        Args:
            assistant_id (str): The ID of the assistant or graph name to run.
            input_data (Optional[Union[str, Dict, list]]): The input data for the run.
            config (Optional[Dict]): The configuration for the assistant.
            metadata (Optional[Dict]): Metadata to assign to the run.
            **kwargs: Additional parameters for the run.
        
        Returns:
            Dict: The output of the run.
        """
        payload = {
            "assistant_id": assistant_id,
            "input": input_data,
            "config": config,
            "metadata": metadata,
        }
        payload.update(kwargs)
    
        url = f"{self.base_url}/runs/wait"
        response = self.session.post(url, json=payload)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print("HTTP Error:", response.status_code, response.text)
            raise e
        return response.json()

    def stream_run(
        self,
        assistant_id: str,
        input_data: Optional[Union[str, Dict, list]] = None,
        config: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        **kwargs
    ) -> requests.Response:
        """
        Stream the output of a stateful or stateless run.

        Args:
            assistant_id (str): The ID of the assistant or graph name to run.
            input_data (Optional[Union[str, Dict, list]]): The input data for the run.
            config (Optional[Dict]): The configuration for the assistant.
            metadata (Optional[Dict]): Metadata to assign to the run.
            **kwargs: Additional parameters for the run.

        Returns:
            requests.Response: The streaming response object.
        """
        payload = {
            "assistant_id": assistant_id,
            "input": input_data,
            "config": config,
            "metadata": metadata,
        }
        payload.update(kwargs)

        url = f"{self.base_url}/runs/stream"
        response = self.session.post(url, json=payload, stream=True)
        response.raise_for_status()
        return response

    def get_run_status(self, thread_id: str, run_id: str) -> Dict:
        """
        Retrieve the status and details of a run.

        Args:
            thread_id (str): The ID of the thread.
            run_id (str): The ID of the run.

        Returns:
            Dict: The details of the run.
        """
        url = f"{self.base_url}/threads/{thread_id}/runs/{run_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def cancel_run(self, thread_id: str, run_id: str, **kwargs) -> None:
        """
        Cancel a running task.
        
        Args:
            thread_id (str): The ID of the thread.
            run_id (str): The ID of the run.
            **kwargs: Additional parameters for canceling the run.
        """
        url = f"{self.base_url}/threads/{thread_id}/runs/{run_id}/cancel"
        response = self.session.post(url, json=kwargs)
        response.raise_for_status()
    

    def get_assistant_details(self, assistant_id: str) -> Dict:
        """
        Fetch details of an assistant, including its configuration and schemas.

        Args:
            assistant_id (str): The ID of the assistant.

        Returns:
            Dict: The details of the assistant.
        """
        url = f"{self.base_url}/assistants/{assistant_id}/schemas"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_thread_state(self, thread_id: str) -> Dict:
        """
        Retrieve the current state of a thread.

        Args:
            thread_id (str): The ID of the thread.

        Returns:
            Dict: The state of the thread.
        """
        url = f"{self.base_url}/threads/{thread_id}/state"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def update_thread_state(self, thread_id: str, values: Dict, checkpoint: Optional[Dict] = None) -> Dict:
        """
        Update the state of a thread with new values.

        Args:
            thread_id (str): The ID of the thread.
            values (Dict): The new values to update the state with.
            checkpoint (Optional[Dict]): The checkpoint to update the state of.

        Returns:
            Dict: The updated state of the thread.
        """
        payload = {
            "values": values,
            "checkpoint": checkpoint,
        }

        url = f"{self.base_url}/threads/{thread_id}/state"
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def put_item(self, namespace: list, key: str, value: Dict) -> None:
        """
        Store a key-value pair in the persistent store.

        Args:
            namespace (list): The namespace path for the item.
            key (str): The key of the item.
            value (Dict): The value of the item.
        """
        payload = {
            "namespace": namespace,
            "key": key,
            "value": value,
        }

        url = f"{self.base_url}/store/items"
        response = self.session.put(url, json=payload)
        response.raise_for_status()

    def get_item(self, namespace: Optional[list] = None, key: str = None) -> Dict:
        """
        Retrieve an item from the persistent store.

        Args:
            namespace (Optional[list]): The namespace path for the item.
            key (str): The key of the item.

        Returns:
            Dict: The retrieved item.
        """
        url = f"{self.base_url}/store/items"
        params = {
            "namespace": namespace,
            "key": key,
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def search_items(
        self,
        namespace_prefix: Optional[list] = None,
        filter: Optional[Dict] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Dict:
        """
        Search for items in the persistent store based on filters.

        Args:
            namespace_prefix (Optional[list]): The namespace prefix to search within.
            filter (Optional[Dict]): A dictionary of key-value pairs to filter results.
            limit (int): The maximum number of items to return.
            offset (int): The number of items to skip before returning results.

        Returns:
            Dict: The search results.
        """
        payload = {
            "namespace_prefix": namespace_prefix,
            "filter": filter,
            "limit": limit,
            "offset": offset,
        }

        url = f"{self.base_url}/store/items/search"
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def create_assistant(
        self,
        graph_id: str,
        assistant_id: Optional[str] = None,
        config: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        name: Optional[str] = None,
        if_exists: str = "raise"
    ) -> Dict:
        """
        Create an assistant.

        Args:
            graph_id (str): The ID of the graph (usually set in your langgraph.json).
            assistant_id (Optional[str]): Optionally specify an assistant ID.
            config (Optional[Dict]): Configuration for the assistant.
            metadata (Optional[Dict]): Metadata to attach to the assistant.
            name (Optional[str]): Name of the assistant.
            if_exists (str): Strategy if an assistant already exists ("raise" or "do_nothing").

        Returns:
            Dict: The created assistant details.
        """
        payload = {
            "graph_id": graph_id,
            "if_exists": if_exists
        }
        if assistant_id is not None:
            payload["assistant_id"] = assistant_id
        if config is not None:
            payload["config"] = config
        if metadata is not None:
            payload["metadata"] = metadata
        if name is not None:
            payload["name"] = name
        url = f"{self.base_url}/assistants"
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()
