import unittest
from flask import Flask
from unittest.mock import patch
from app import create_app

class TestIntegrationDashboard(unittest.TestCase):
    def setUp(self):
        """
        Configuración inicial para la prueba.
        Crea una aplicación Flask y un cliente de pruebas.
        """
        self.app = create_app()
        self.client = self.app.test_client()


def test_dashboard_render_with_mocked_data(test_client):
    with patch("app.modules.public.routes.DataSetService") as MockDataSetService, \
         patch("app.modules.public.routes.FeatureModelService") as MockFeatureModelService:
        
        MockDataSetService.return_value.count_synchronized_datasets.return_value = 10
        MockFeatureModelService.return_value.count_feature_models.return_value = 5
        MockDataSetService.return_value.total_dataset_downloads.return_value = 100
        MockFeatureModelService.return_value.total_feature_model_downloads.return_value = 50
        MockDataSetService.return_value.total_dataset_views.return_value = 200
        MockFeatureModelService.return_value.total_feature_model_views.return_value = 150

        login_response = test_client.post("/login", json={"username": "test_user", "password": "password123"})
        assert login_response.status_code == 200, "Login was unsuccessful."

        response = test_client.get("/dashboard")
        assert response.status_code == 200, "The dashboard could not be accessed."

        response_data = response.data.decode("utf-8")
        assert "10" in response_data, "datasets_counter not found in dashboard."
        assert "5" in response_data, "feature_models_counter not found in dashboard."
        assert "100" in response_data, "total_dataset_downloads not found in dashboard."
        assert "50" in response_data, "total_feature_model_downloads not found in dashboard."
        assert "200" in response_data, "total_dataset_views not found in dashboard."
        assert "150" in response_data, "total_feature_model_views not found in dashboard."

if __name__ == "__main__":
    unittest.main()
