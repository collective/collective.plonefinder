from plone.testing import z2
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting


import collective.plonefinder


COLLECTIVE_PLONEFINDER = PloneWithPackageLayer(
    zcml_package=collective.plonefinder,
    zcml_filename='configure.zcml',
    gs_profile_id='collective.plonefinder:default',
    name='COLLECTIVE_PLONEFINDER'
)

COLLECTIVE_PLONEFINDER_INTEGRATION = IntegrationTesting(
    bases=(COLLECTIVE_PLONEFINDER, ),
    name="COLLECTIVE_PLONEFINDER_INTEGRATION"
)

COLLECTIVE_PLONEFINDER_FUNCTIONAL = FunctionalTesting(
    bases=(COLLECTIVE_PLONEFINDER, ),
    name="COLLECTIVE_PLONEFINDER_FUNCTIONAL"
)
