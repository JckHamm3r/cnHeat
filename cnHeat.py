import requests

class cnHeat:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_endpoint = "https://internal.cnheat.cambiumnetworks.com/api/v1/"
        self.token = self._authenticate()
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.sites = self.get_sites()
        self.predictions = self.get_predictions()
        self.users = self.get_users()

    def _authenticate(self):
        """
        Authenticates the client using client_id and client_secret.
        
        Returns:
            str: Access token used for authenticated API requests.
        
        Raises:
            RuntimeError: If authentication fails.
        """
        auth_url = f"{self.base_endpoint}oauth/token"
        data = {"client_id": self.client_id, "client_secret": self.client_secret}

        try:
            response = requests.post(auth_url, data=data)
            response.raise_for_status()
            return response.json().get("access_token")
        except requests.RequestException as e:
            # You could log this in production
            raise RuntimeError(f"Authentication failed: {e}")

    def get_credits(self):
        """
        Retrieves and formats credit information from the API.
        
        Returns:
            dict: A dictionary containing credit types and their quantities.
        
        Raises:
            RuntimeError: If fetching credits fails.
        """
        try:
            response = requests.get(f"{self.base_endpoint}credits", headers=self.headers)
            response.raise_for_status()
            credit_data = response.json()
            return credit_data
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch credits: {e}")

    def get_antennas(self, freq):
        """
        Retrieves antenna options for a specified frequency.
        
        Args:
            freq (float): The frequency for which to retrieve antennas.
        
        Returns:
            dict: A dictionary of antennas available for the specified frequency.
        
        Raises:
            RuntimeError: If fetching antennas fails.
        """
        try:
            response = requests.get(f"{self.base_endpoint}antennas", headers=self.headers, params={"frequency": freq})
            response.raise_for_status()
            antenna_data = response.json()
            antennas = antenna_data.get('objects', [])
            return antennas
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch antennas: {e}")

####### RADIOS ########

    def get_site_radios(self, site_id):
        """
        Retrieves a list of radios associated with a given site ID.

        Args:
            site_id (str): The ID of the site whose radios are to be retrieved.

        Returns:
            dict: A dictionary containing the site name and a dictionary of radios with their IDs and names.

        Raises:
            RuntimeError: If fetching the radios fails.
        """
        try:
            response = requests.get(f"{self.base_endpoint}radios/{site_id}", headers=self.headers)
            response.raise_for_status()
            radio_data = response.json()
            radios = radio_data.get('objects', [])
            return radios
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch {self.sites[site_id]['name']} radios: {e}")

    def get_radio(self, radio_id):
        """
        Retrieves details for a specific radio by its ID.

        Args:
            radio_id (str): The ID of the radio to retrieve.

        Returns:
            dict: The response from the API containing radio details.

        Raises:
            RuntimeError: If fetching the radio fails.
        """
        try:
            response = requests.get(f"{self.base_endpoint}radio/{radio_id}", headers=self.headers)
            response.raise_for_status()
            return response.json() 
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch radio: {e}")

    def delete_radio(self, radio_id):
            """
            Deletes a specific radio by its ID.

            Args:
                radio_id (str): The ID of the radio to delete.

            Returns:
                dict: The response from the API containing radio deletion details.

            Raises:
                RuntimeError: If deleting the radio fails.
            """
            try:
                response = requests.delete(f"{self.base_endpoint}radio/{radio_id}", headers=self.headers)
                response.raise_for_status()
                return response.json() 
            except requests.RequestException as e:
                raise RuntimeError(f"Failed to delete radio: {e}")

    def create_radio(self, site_id, freq, antennaId, azimuth, aglHeightMeters=20, radioName=None, folliageTuning=-1, arHeightMeters=0, radiusMeters=12875, smGain=18.5, tilt=-2, txClearanceMeters=30, txPowerDbm=27.2):
        """
        Creates a new radio at a site with provided configuration.
        
        Args:
            site_id (str): The ID of the site where the radio will be created.
            freq (float): The frequency of the radio.
            antennaId (str): The ID of the antenna to use.
            azimuth (float): The azimuth angle for the radio.
            aglHeightMeters (float, optional): Height above ground level in meters. Defaults to 20.
            radioName (str, optional): Custom name for the radio. Defaults to None.
            folliageTuning (float, optional): Foliage tuning value. Defaults to -1.
            arHeightMeters (float, optional): Rooftop height in meters. Defaults to 0.
            radiusMeters (float, optional): Radius in meters. Defaults to 12875.
            smGain (float, optional): Gain in dBi. Defaults to 18.5.
            tilt (float, optional): Tilt value. Defaults to -2.
            txClearanceMeters (float, optional): TX clearance in meters. Defaults to 50.
            txPowerDbm (float, optional): TX power in dBm. Defaults to 27.2.
        
        Returns:
            dict: The response from the API after radio creation.
        
        Raises:
            RuntimeError: If radio creation fails.
        """
        try:
            antennas = self.get_antennas(freq)
            sites = self.get_sites()
            if radioName is None:
                for s in sites:
                    if s['id'] == site_id:
                        site_name = s['name']
                        break
                for a in antennas:
                    if a['id'] == antennaId:
                        antenna_name = a['antenna']
                        break
                radioName = f"""AP-{antenna_name.split("-")[0]}-{azimuth}-{str(freq).split(".")[0]} GHZ.{site_name.upper()}"""
            data = {
                "antenna": antennaId,
                "name": radioName,
                "azimuth": azimuth,
                "foliage_tuning": folliageTuning,
                "frequency(ghz)": freq,
                "height(m)": aglHeightMeters,
                "height_rooftop(m)": arHeightMeters,
                "radius(m)": radiusMeters,
                "sm_gain(dbi)": smGain,
                "tilt": tilt,
                "txclearance(m)": txClearanceMeters,
                "txpower(dbm)": txPowerDbm
            }
            response = requests.post(f"{self.base_endpoint}radio/{site_id}", headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to create radio: {e}") 

    def update_radio(self, radio_id, freq, antennaId, azimuth, aglHeightMeters=20, radioName=None, folliageTuning=-1, arHeightMeters=0, radiusMeters=12875, smGain=18.5, tilt=-2, txClearanceMeters=30, txPowerDbm=27.2):
        """
        Updates an existing radio with provided configuration.
        
        Args:
            radio_id (str): The ID of the radio to be updated.
            freq (float): The frequency of the radio.
            antennaId (str): The ID of the antenna to use.
            azimuth (float): The azimuth angle for the radio.
            aglHeightMeters (float, optional): Height above ground level in meters. Defaults to 20.
            radioName (str, optional): Custom name for the radio. Defaults to None.
            folliageTuning (float, optional): Foliage tuning value. Defaults to -1.
            arHeightMeters (float, optional): Rooftop height in meters. Defaults to 0.
            radiusMeters (float, optional): Radius in meters. Defaults to 12875.
            smGain (float, optional): Gain in dBi. Defaults to 18.5.
            tilt (float, optional): Tilt value. Defaults to -2.
            txClearanceMeters (float, optional): TX clearance in meters. Defaults to 50.
            txPowerDbm (float, optional): TX power in dBm. Defaults to 27.2.
        
        Returns:
            dict: The response from the API after radio update.
        
        Raises:
            RuntimeError: If radio update fails.
        """
        try:
            if radioName is None:
                radioName = "No Name"
            data = {
                "antenna": antennaId,
                "name": radioName,
                "azimuth": azimuth,
                "foliage_tuning": folliageTuning,
                "frequency(ghz)": freq,
                "height(m)": aglHeightMeters,
                "height_rooftop(m)": arHeightMeters,
                "radius(m)": radiusMeters,
                "sm_gain(dbi)": smGain,
                "tilt": tilt,
                "txclearance(m)": txClearanceMeters,
                "txpower(dbm)": txPowerDbm
            }
            response = requests.patch(f"{self.base_endpoint}radio/{radio_id}", headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to update radio: {e}")

####### SITES ########

    def get_sites(self):
        """
        Fetches a list of sites and their metadata from the API.
        
        Returns:
            dict: A dictionary of sites with their details.
        
        Raises:
            RuntimeError: If fetching sites fails.
        """
        try:
            response = requests.get(f"{self.base_endpoint}sites", headers=self.headers)
            response.raise_for_status()
            site_data = response.json()
            sites = site_data.get('objects', [])
            return sites
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch sites: {e}")

    def rename_site(self, site_id, name):
        """
        Updates a new site with specified details.
        
        Args:
            name (str): The name of the site.
        
        Returns:
            dict: The response from the API after site update.
        
        Raises:
            RuntimeError: If site update fails.
            """
        try:
            data = {
                "name": name,
            }
            response = requests.patch(f"{self.base_endpoint}site/{site_id}", headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to update site: {e}")

    def create_site(self, name, lat, lon, credit_id):
        """
        Creates a new site with specified details.
        
        Args:
            name (str): The name of the site.
            lat (float): The latitude of the site.
            lon (float): The longitude of the site.
            credit_id (str): The ID of the credit to associate with the site.
        
        Returns:
            dict: The response from the API after site creation.
        
        Raises:
            RuntimeError: If site creation fails.
        """
        try:
            data = {
                "name": name,
                "lat": lat,
                "lon": lon,
                "credits": credit_id
            }
            response = requests.post(f"{self.base_endpoint}sites", headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to create site: {e}")

####### PREDICTIONS ########
        
    def get_predictions(self):
        """
        Fetches a list of predictions from the API.

        Returns:
            list: A list of prediction objects.
        
        Raises:
            RuntimeError: If fetching predictions fails.
        """
        try:
            response = requests.get(f"{self.base_endpoint}predictions", headers=self.headers)
            response.raise_for_status()
            predictions = response.json().get('objects', [])
            return predictions
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch predicitions: {e}")
        
    def create_prediction(self, prediction_name, radio_id_list):
        """
        Creates a prediction using a list of radio IDs.

        Args:
            prediction_name (str): Name of the prediction.
            radio_id_list (list): List of radio IDs to include.

        Returns:
            dict: The API response with the new prediction details.

        Raises:
            RuntimeError: If creating prediction fails.
        """
        data = {
            "name":prediction_name,
            "radio_list":radio_id_list
        }
        try:
            response = requests.post(f"{self.base_endpoint}predictions", headers=self.headers, json=data)
            response.raise_for_status()
            return response.json() 
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to create predicition: {e}")
        
    def get_predictions_statuses(self):
        """
        Retrieves prediction job statuses from the API.

        Returns:
            list: A list of prediction status objects.

        Raises:
            RuntimeError: If fetching statuses fails.
        """
        try:
            response = requests.get(f"{self.base_endpoint}predictions/jobmanagement", headers=self.headers)
            response.raise_for_status()
            predictions_statuses = response.json().get('objects', [])
            return predictions_statuses
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch predicition statuses: {e}")

    def rename_prediction(self, prediction_id, new_name):
        """
        Renames a prediction by its ID.

        Args:
            prediction_id (str): ID of the prediction.
            new_name (str): New name for the prediction.

        Returns:
            dict: API response after renaming.

        Raises:
            RuntimeError: If renaming fails.
        """
        data = {
            "name":new_name,
        }
        try:
            response = requests.patch(f"{self.base_endpoint}prediction/{prediction_id}/rename", headers=self.headers, json=data)
            response.raise_for_status()
            return response.json() 
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to rename predicition: {e}")
        
    def delete_prediction(self, prediction_id):
        """
        Deletes a prediction by its ID.

        Args:
            prediction_id (str): ID of the prediction to delete.

        Returns:
            dict: API response after deletion.

        Raises:
            RuntimeError: If deletion fails.
        """
        try:
            response = requests.delete(f"{self.base_endpoint}prediction/{prediction_id}", headers=self.headers)
            response.raise_for_status()
            return response.json() 
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to delete predicition: {e}")

####### USERS ########

    def get_users(self):
        """
        Retrieves a list of users from the API.

        Returns:
            list: A list of user objects.

        Raises:
            RuntimeError: If the request fails.
        """
        try:
            response = requests.get(f"{self.base_endpoint}users", headers=self.headers)
            response.raise_for_status()
            return response.json().get('objects', [])
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to get users: {e}")
        
    def add_user(self, email, role):
        """
        Adds a new user with a specified role.

        Args:
            email (str): Email of the user.
            role (str): Role or permission level.

        Returns:
            dict: API response after user is added.

        Raises:
            RuntimeError: If adding the user fails.
        """
        data = {
            "email":email,
            "permission":role,
        }
        try:
            response = requests.post(f"{self.base_endpoint}users", headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to add user: {e}")
        
    def delete_user(self, email):
        """
        Deletes a user based on email.

        Args:
            email (str): Email of the user to delete.

        Returns:
            dict: API response after deletion.

        Raises:
            RuntimeError: If deletion fails.
        """
        data = {
            "email":email
        }
        try:
            response = requests.delete(f"{self.base_endpoint}user", headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to delete user: {e}")

####### SUBSCRIPTIONS ########

    def get_subscriptions(self):
        """
        Retrieves a list of active subscriptions.

        Returns:
            list: A list of subscription objects.

        Raises:
            RuntimeError: If fetching subscriptions fails.
        """
        try:
            response = requests.get(f"{self.base_endpoint}subscriptions", headers=self.headers)
            response.raise_for_status()
            return response.json().get('objects', [])
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to get subscriptions: {e}")
        
    def renew_subscriptions(self, site_id):
        """
        Renews a subscription for a given site.

        Args:
            site_id (str): ID of the site.

        Returns:
            dict: API response after renewal.

        Raises:
            RuntimeError: If renewal fails.
        """
        try:
            response = requests.patch(f"{self.base_endpoint}subscription/{site_id}/renew", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to renew subscription: {e}")
        
    def terminate_subscription(self, site_id):
        """
        Terminates a subscription for a given site.

        Args:
            site_id (str): ID of the site.

        Returns:
            dict: API response after termination.

        Raises:
            RuntimeError: If termination fails.
        """
        try:
            response = requests.patch(f"{self.base_endpoint}subscription/{site_id}/terminate", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to renew subscription: {e}")

