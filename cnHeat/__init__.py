import requests
import httpx

class cnHeat:
    def __init__(self, client_id, client_secret, base_endpoint="https://internal.cnheat.cambiumnetworks.com/api/v1/"):
        self.get_antennas = self.AntennaFetcher(self)
        self.get_site_radios = self.SiteRadiosFetcher(self)
        self.get_sites = self.SitesFetcher(self)
        self.get_predictions = self.PredictionsFetcher(self)
        self.get_users = self.UsersFetcher(self)
        self.get_subscriptions = self.SubscriptionsFetcher(self)
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_endpoint = base_endpoint
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

    class AntennaFetcher:
        def __init__(self, outer):
            self.outer = outer  # Reference to the parent cnHeat instance

        def __call__(self, freq):
            """
            Retrieves antenna options for a specified frequency.

            Args:
                freq (float): The frequency for which to retrieve antennas.

            Returns:
                list: A list of antennas available for the specified frequency.

            Raises:
                RuntimeError: If fetching antennas fails.
            """
            try:
                response = requests.get(
                    f"{self.outer.base_endpoint}antennas",
                    headers=self.outer.headers,
                    params={"frequency": freq}
                )
                response.raise_for_status()
                antenna_data = response.json()
                return antenna_data.get('objects', [])
            except requests.RequestException as e:
                raise RuntimeError(f"Failed to fetch antennas: {e}")

        def to_dict(self, freq, key=None):
            """
            Returns a dictionary of antennas keyed by antenna ID.

            Args:
                freq (float): The frequency for which to retrieve antennas.

            Returns:
                dict: A dictionary mapping antenna ID to antenna data.
            """
            antennas = self(freq)
            if key == None:
                return {a['id']: a for a in antennas if 'id' in a}
            else:
                return {a[key]: a for a in antennas if key in a}

####### RADIOS ########

    class SiteRadiosFetcher:
        def __init__(self, outer):
            self.outer = outer

        def __call__(self, site_id):
            """
            Retrieves a list of radios associated with a given site ID.

            Args:
                site_id (str): The ID of the site whose radios are to be retrieved.

            Returns:
                list: A list of radios for the site.

            Raises:
                RuntimeError: If fetching the radios fails.
            """
            try:
                response = requests.get(
                    f"{self.outer.base_endpoint}radios/{site_id}",
                    headers=self.outer.headers
                )
                response.raise_for_status()
                radio_data = response.json()
                return radio_data.get('objects', [])
            except requests.RequestException as e:
                # fallback if site info isn't indexed by ID
                site_name = site_id
                for s in self.outer.sites:
                    if s['id'] == site_id:
                        site_name = s['name']
                raise RuntimeError(f"Failed to fetch {site_name} radios: {e}")

        def to_dict(self, site_id, key=None):
            """
            Returns radios for a site as a dictionary keyed by radio ID.

            Args:
                site_id (str): The ID of the site.

            Returns:
                dict: Dictionary of radios by ID.
            """
            radios = self(site_id)
            if key == None:
                return {r['id']: r for r in radios if 'id' in r}
            else:
                return {r[key]: r for r in radios if key in r}

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

    def create_radio(self, site_id, freq, antennaId, azimuth, aglHeightMeters=20, radioName=None, foliageTuning=-1, arHeightMeters=0, radiusMeters=12875, smGain=18.5, tilt=-2, txClearanceMeters=30, txPowerDbm=27.2):
        """
        Creates a new radio at a site with provided configuration.
        
        Args:
            site_id (str): The ID of the site where the radio will be created.
            freq (float): The frequency of the radio.
            antennaId (str): The ID of the antenna to use.
            azimuth (float): The azimuth angle for the radio.
            aglHeightMeters (float, optional): Height above ground level in meters. Defaults to 20.
            radioName (str, optional): Custom name for the radio. Defaults to None.
            foliageTuning (float, optional): Foliage tuning value. Defaults to -1.
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
                site_name = next((s['name'] for s in sites if s['id'] == site_id), "UnknownSite")
                antenna_name = next((a['antenna'] for a in antennas if a['id'] == antennaId), "UnknownAntenna")
                radioName = f"""AP-{antenna_name.split("-")[0]}-{azimuth}-{str(freq).split(".")[0]} GHZ.{site_name.upper()}"""
            data = {
                "antenna": antennaId,
                "name": radioName,
                "azimuth": azimuth,
                "foliage_tuning": foliageTuning,
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

    def update_radio(self, radio_id, data):
        """
        Updates an existing radio with only the fields provided in the `data` dictionary.
    
        Args:
            radio_id (str): The ID of the radio to update.
            data (dict): Dictionary of fields to update. Only these fields will be patched.
                Valid keys include:
                    - "frequency(ghz)" (float): Frequency in GHz
                    - "antenna" (str): Antenna ID
                    - "azimuth" (float): Azimuth angle
                    - "height(m)" (float): Height above ground level in meters
                    - "name" (str or None): Radio name
                    - "foliage_tuning" (float): Foliage tuning value
                    - "height_rooftop(m)" (float): Rooftop height in meters
                    - "radius(m)" (float): Coverage radius in meters
                    - "sm_gain(dbi)" (float): Subscriber module gain in dBi
                    - "tilt" (float): Antenna tilt value
                    - "txclearance(m)" (float): TX clearance in meters
                    - "txpower(dbm)" (float): TX power in dBm
    
        Returns:
            dict: API response after updating the radio.
    
        Raises:
            RuntimeError: If the radio update fails.
        """
        try:

            response = requests.patch(
                f"{self.base_endpoint}radio/{radio_id}",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to update radio: {e}")

####### SITES ########

    class SitesFetcher:
        def __init__(self, outer):
            self.outer = outer

        def __call__(self):
            """
            Fetches a list of sites and their metadata from the API.

            Returns:
                list: A list of site objects.

            Raises:
                RuntimeError: If fetching sites fails.
            """
            try:
                response = requests.get(
                    f"{self.outer.base_endpoint}sites",
                    headers=self.outer.headers
                )
                response.raise_for_status()
                site_data = response.json()
                return site_data.get('objects', [])
            except requests.RequestException as e:
                raise RuntimeError(f"Failed to fetch sites: {e}")

        def to_dict(self, key):
            """
            Returns sites as a dictionary keyed by site ID.

            Returns:
                dict: Dictionary of sites by ID.
            """
            sites = self()
            if key == None:
                return {s['id']: s for s in sites if 'id' in s}
            else:
                return {s[key]: s for s in sites if key in s}

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
            self.sites = self.get_sites()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to create site: {e}")

####### PREDICTIONS ########
        
    class PredictionsFetcher:
        def __init__(self, outer):
            self.outer = outer

        def __call__(self):
            """
            Fetches a list of predictions from the API.

            Returns:
                list: A list of prediction objects.

            Raises:
                RuntimeError: If fetching predictions fails.
            """
            try:
                response = requests.get(
                    f"{self.outer.base_endpoint}predictions",
                    headers=self.outer.headers
                )
                response.raise_for_status()
                return response.json().get('objects', [])
            except requests.RequestException as e:
                raise RuntimeError(f"Failed to fetch predictions: {e}")

        def to_dict(self, key=None):
            """
            Returns predictions as a dictionary keyed by prediction ID.

            Returns:
                dict: Dictionary of predictions by ID.
            """
            predictions = self()
            if key == None:
                return {p['id']: p for p in predictions if 'id' in p}
            else:
                return {p[key]: p for p in predictions if key in p}

    def create_eval_prediction(self, prediction_name, radio_id_list, install_height, install_reference):
        """
        Creates a prediction using a list of radio IDs.

        Args:
            prediction_name (str): Name of the prediction.
            radio_id_list (list): List of radio IDs to include.
            install_height: CPE height above reference.
            install_reference: Ground or Roof

        Returns:
            dict: The API response with the new prediction details.

        Raises:
            RuntimeError: If creating prediction fails.
        """
        data = {
            "name":prediction_name,
            "radio_list":radio_id_list,
            "install_height":install_height,
            "install_reference":install_reference
        }
        try:
            response = requests.post(f"{self.base_endpoint}predictions", headers=self.headers, json=data)
            response.raise_for_status()
            self.predictions = self.get_predictions()
            return response.json() 
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to create predicition: {e}")
    
        
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
            self.predictions = self.get_predictions()
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
            self.predictions = self.get_predictions()
            return response.json() 
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to delete predicition: {e}")

####### USERS ########

    class UsersFetcher:
        def __init__(self, outer):
            self.outer = outer

        def __call__(self):
            """
            Retrieves a list of users from the API.

            Returns:
                list: A list of user objects.

            Raises:
                RuntimeError: If the request fails.
            """
            try:
                response = requests.get(
                    f"{self.outer.base_endpoint}users",
                    headers=self.outer.headers
                )
                response.raise_for_status()
                return response.json().get('objects', [])
            except requests.RequestException as e:
                raise RuntimeError(f"Failed to get users: {e}")

        def to_dict(self, key=None):
            """
            Returns users as a dictionary keyed by user ID.

            Returns:
                dict: Dictionary of users by ID.
            """
            users = self()
            if key == None:
                return {u['email']: u for u in users if 'email' in u}
            else:
                return {u[key]: u for u in users if key in u}
        
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
            self.users = self.get_users()
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
            self.users = self.get_users()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to delete user: {e}")

####### SUBSCRIPTIONS ########

    class SubscriptionsFetcher:
        def __init__(self, outer):
            self.outer = outer

        def __call__(self):
            """
            Retrieves a list of active subscriptions.

            Returns:
                list: A list of subscription objects.

            Raises:
                RuntimeError: If fetching subscriptions fails.
            """
            try:
                response = requests.get(
                    f"{self.outer.base_endpoint}subscriptions",
                    headers=self.outer.headers
                )
                response.raise_for_status()
                return response.json().get('objects', [])
            except requests.RequestException as e:
                raise RuntimeError(f"Failed to get subscriptions: {e}")

        def to_dict(self, key=None):
            """
            Returns subscriptions as a dictionary keyed by subscription ID.

            Returns:
                dict: Dictionary of subscriptions by ID.
            """
            subscriptions = self()
            if key == None:
                return {s['id']: s for s in subscriptions if 'id' in s}
            else:
                return {s[key]: s for s in subscriptions if key in s}
        
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
            raise RuntimeError(f"Failed to terminate subscription: {e}")

    def create_site_export(self, tower_name, service_id, auth_token, project_id, providerid, technology_code, cpe_heigth_meters):
        """
        Creates a CNHeat export job for a given tower.
    
        Args:
            tower_name (str): The name of the tower/site.
            service_id (str): The service location (SL) ID associated with the tower.
            auth_token (str): Bearer token for authentication, pulled from browser DevTools.
            project_id (str): The project/export ID (UUID at the end of the export URL).
            providerid (int): Cambium-assigned provider ID used in the export payload.
    
        Returns:
            None. Prints the response from the export endpoint.
        """
        heatsites = self.get_sites.to_dict("name")
        radios = self.get_site_radios(heatsites[tower_name]['id'])
    
        sl_mappings = [[service_id, r["id"]] for r in radios]
    
        payload = {
            "name": tower_name,
            "description": tower_name,
            "mmwave": False,
            "providerid": providerid,
            "brandname": f"{tower_name}",
            "technology": technology_code,
            "lowlatency": True,
            "bizrescode": "X",
            "rxheight": cpe_heigth_meters,
            "subscribers": "",
            "sl_ap_mappings": sl_mappings,
            "nlos": True
        }
    
        url = f"https://internal.cnheat.cambiumnetworks.com/export/{project_id}"
    
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': f'Bearer {auth_token}',
            'cache-control': 'no-cache',
            'content-type': 'application/json; charset=utf-8',
            'origin': 'https://cnheat.cambiumnetworks.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://cnheat.cambiumnetworks.com/',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0'
        }

    with httpx.Client(http2=True) as client:
        response = client.post(url, headers=headers, json=payload)
        print("Status Code:", response.status_code)
        print("Response:", response.text)

