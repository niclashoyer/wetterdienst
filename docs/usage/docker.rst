Docker
######

Wetterdienst comes in two Docker image flavors. A "standard" variant, including
all dependency packages from the ``export,restapi`` extras, and a "full" variant,
including all dependency packages from the ``export,influxdb,cratedb,postgresql,
radar,bufr,restapi,explorer,radar,radarplus`` extras.


Acquire image
*************

Get ``wetterdienst-standard``:

.. code-block:: bash

    docker pull ghcr.io/earthobservations/wetterdienst-standard

Get ``wetterdienst-full``:

.. code-block:: bash

    docker pull ghcr.io/earthobservations/wetterdienst-full


Invoke
******

Run Wetterdienst command line interface:

.. code-block:: bash

    docker run -it --rm ghcr.io/earthobservations/wetterdienst-standard wetterdienst --version

Run Wetterdienst HTTP REST API service:

.. code-block:: bash

    docker run -it --rm --publish=7890:7890 ghcr.io/earthobservations/wetterdienst-standard wetterdienst restapi --listen 0.0.0.0:7890

Run Wetterdienst Explorer UI service:

.. code-block:: bash

    docker run -it --rm --publish=7891:7891 ghcr.io/earthobservations/wetterdienst-full wetterdienst explorer --listen 0.0.0.0:7891
