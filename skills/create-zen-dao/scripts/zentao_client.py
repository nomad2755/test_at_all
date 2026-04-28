#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ZenTao API Client
A client for interacting with ZenTao (禅道) API for bug tracking and project management.
"""

import requests
import json
from typing import Optional, Dict, Any


class ZenTaoClient:
    """ZenTao API Client"""

    def __init__(self, base_url: str = "http://192.168.0.28:9980"):
        """
        Initialize ZenTao client

        Args:
            base_url: ZenTao server address
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api.php/v1"
        self.token: Optional[str] = None

    def login(self, account: str, password: str) -> bool:
        """
        Login to ZenTao and obtain token

        Args:
            account: Username
            password: Password

        Returns:
            bool: Whether login was successful
        """
        url = f"{self.api_base}/tokens"
        payload = {
            "account": account,
            "password": password
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            result = response.json()
            self.token = result.get('token')

            if self.token:
                print(f"Login successful, token: {self.token[:10]}...")
                return True
            else:
                print(f"Login failed: {result}")
                return False

        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return False

    def submit_bug(self, product_id: int, bug_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Submit a bug to ZenTao

        Args:
            product_id: Product ID
            bug_data: Bug data dictionary

        Returns:
            Dict: API response result or None on failure
        """
        if not self.token:
            print("Not logged in. Please call login() first.")
            return None

        url = f"{self.api_base}/products/{product_id}/bugs"
        headers = {
            "Token": self.token,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=bug_data, headers=headers, timeout=10)
            response.raise_for_status()

            result = response.json()
            print(f"Bug submitted successfully: {result}")
            return result

        except requests.RequestException as e:
            print(f"Bug submission failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
            return None

    def get_products(self) -> Optional[Dict]:
        """
        Get list of products

        Returns:
            Dict: API response with product list
        """
        if not self.token:
            print("Not logged in. Please call login() first.")
            return None

        url = f"{self.api_base}/products"
        headers = {
            "Token": self.token,
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"Failed to get products: {e}")
            return None

    def get_bugs(self, product_id: int) -> Optional[Dict]:
        """
        Get list of bugs for a product

        Args:
            product_id: Product ID

        Returns:
            Dict: API response with bug list
        """
        if not self.token:
            print("Not logged in. Please call login() first.")
            return None

        url = f"{self.api_base}/products/{product_id}/bugs"
        headers = {
            "Token": self.token,
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"Failed to get bugs: {e}")
            return None


def main():
    """Main function: Demonstrate complete login and submit workflow"""

    # Initialize client
    client = ZenTaoClient("http://192.168.0.28:9980")

    # Step 1: Login to get token
    login_success = client.login(
        account="shidawei",
        password="shidawei"
    )

    if not login_success:
        print("Login failed, program terminated")
        return

    # Step 2: Construct bug data
    bug_data = {
        "title": "ZenTao Agent Bug Submission Test",
        "severity": 2,
        "pri": 1,
        "project": 1,
        "execution": 17,
        "type": "codeerror",
        "openedBuild": ["trunk"],
        "assignedTo": "石大卫",
        "steps": "Bug steps from ZenTao Agent..."
    }

    # Step 3: Submit bug
    result = client.submit_bug(
        product_id=1,
        bug_data=bug_data
    )

    if result:
        print("\n=== Submission Successful ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("\n=== Submission Failed ===")


if __name__ == "__main__":
    main()
