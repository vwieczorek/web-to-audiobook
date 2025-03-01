import logging
import time
from typing import Dict, Optional, Any, Union

import httpx


class HttpClient:
    """HTTP client with retry logic and error handling."""
    
    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: float = 10.0,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the HTTP client.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            timeout: Request timeout in seconds
            logger: Logger instance to use. If None, a default logger will be created.
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.logger = logger or logging.getLogger(self.__class__.__name__)
    
    async def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        retry_codes: Optional[list] = None
    ) -> Union[httpx.Response, Exception]:
        """
        Make an HTTP request with retry logic.
        
        Args:
            method: HTTP method to use (GET, POST, etc.)
            url: URL to request
            headers: Request headers
            params: Query parameters
            json: JSON body
            data: Request body data
            retry_codes: HTTP status codes to retry on, defaults to [429, 500, 502, 503, 504]
            
        Returns:
            Response object if successful, Exception if all retries failed
        """
        if retry_codes is None:
            retry_codes = [429, 500, 502, 503, 504]
            
        headers = headers or {}
        retry_count = 0
        last_exception = None
        
        while retry_count <= self.max_retries:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        params=params,
                        json=json,
                        data=data
                    )
                    
                    # Check if we should retry based on status code
                    if response.status_code in retry_codes:
                        retry_count += 1
                        if retry_count > self.max_retries:
                            self.logger.warning(
                                f"Max retries reached for {url}. Last status code: {response.status_code}"
                            )
                            return response
                        
                        # Calculate delay with exponential backoff
                        delay = self.retry_delay * (2 ** (retry_count - 1))
                        self.logger.info(
                            f"Retrying request to {url} due to status code {response.status_code}. "
                            f"Retry {retry_count}/{self.max_retries}. Waiting {delay:.2f}s"
                        )
                        time.sleep(delay)
                        continue
                    
                    # Return successful response
                    return response
                    
            except httpx.RequestError as e:
                last_exception = e
                retry_count += 1
                
                if retry_count > self.max_retries:
                    self.logger.error(f"Max retries reached for {url}. Last error: {str(e)}")
                    return e
                
                # Calculate delay with exponential backoff
                delay = self.retry_delay * (2 ** (retry_count - 1))
                self.logger.warning(
                    f"Request to {url} failed with error: {str(e)}. "
                    f"Retry {retry_count}/{self.max_retries}. Waiting {delay:.2f}s"
                )
                time.sleep(delay)
                
        return last_exception or Exception(f"Unknown error occurred while requesting {url}")