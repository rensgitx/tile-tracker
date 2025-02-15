# Generated by Django 5.1.6 on 2025-02-12 17:52

from django.db import migrations


class Migration(migrations.Migration):

    def load_data(apps, schema_editor):
        UserPOI = apps.get_model("trackapp", "UserPOI")
        data = [
            ["name", "latitude", "longitude", "address", "city", "country"],
            [
                "CN Tower",
                43.6425701,
                -79.3896317290,
                "Bremner Blvd",
                "Toronto",
                "Canada",
            ],
            [
                "Red pandas in Toronto Zoo",
                43.8178807,
                -79.2038913,
                "",
                "Scarborough",
                "Canada",
            ],
            [
                "Toronto Botanical Garden",
                43.7338077,
                -79.3604989,
                "777 Lawrence Ave E",
                "Toronto",
                "Canada",
            ],
            ["High Park", 43.6444384, -79.4679243, "", "Toronto", "Canada"],
            [
                "Centre Island",
                43.6367449,
                -79.4057144,
                "Centre Island",
                "Toronto",
                "Canada",
            ],
        ]
        for ix, row in enumerate(data):
            if ix == 0:
                labels = row
            else:
                UserPOI(**{name: val for name, val in zip(labels, row)}).save()

    dependencies = [
        ("trackapp", "0001_initial"),
    ]

    operations = [migrations.RunPython(load_data)]
