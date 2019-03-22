import os
import logging
from functools import reduce
from operator import mul
from itertools import cycle

from sentry_sdk import configure_scope
from pywps import Process
from pywps import ComplexInput, ComplexOutput, FORMATS, LiteralInput
from pywps.app.Common import Metadata
# import eggshell.general.utils
# from eggshell.log import init_process_logger
from unidecode import unidecode
import requests
import xarray as xr

LOGGER = logging.getLogger("PYWPS")


class XclimIndicatorProcess(Process):

    def __init__(self, xci):
        """Create a WPS process from an xclim indicator class instance."""
        self.xci = xci

        attrs = xci.json()

        outputs = [
            ComplexOutput('output_netcdf', 'Function output in netCDF',
                          abstract="The indicator values computed on the original input grid.",
                          as_reference=True,
                          supported_formats=[FORMATS.NETCDF]
                          ),

            ComplexOutput('output_log', 'Logging information',
                          abstract="Collected logs during process run.",
                          as_reference=True,
                          supported_formats=[FORMATS.TEXT]),
        ]

        identifier = attrs['identifier']
        super(XclimIndicatorProcess, self).__init__(
            self._handler,
            identifier=identifier,
            version='0.1',
            title=unidecode(attrs['long_name']),
            abstract=unidecode(attrs['abstract']),
            inputs=self.load_inputs(eval(attrs['parameters'])),
            outputs=outputs,
            status_supported=True,
            store_supported=True,
        )

    def load_inputs(self, params):
        # Ideally this would be based on the Parameters docstring section rather than name conventions.
        inputs = []

        for name, attrs in params.items():
            if name in ['tas', 'tasmin', 'tasmax', 'pr', 'prsn']:
                inputs.append(make_nc_input(name))
            elif name in ['tn10', 'tn90']:
                inputs.append(make_nc_input(name))
            elif name in ['thresh_tasmin', 'thresh_tasmax']:
                inputs.append(make_thresh(name, attrs['default'], attrs['desc']))
            elif name in ['thresh', ]:
                inputs.append(make_thresh(name, attrs['default'], attrs['desc']))
            elif name in ['freq', ]:
                inputs.append(make_freq(name, attrs['default']))
            elif name in ['window', ]:
                inputs.append(make_window(name, attrs['default'], attrs['desc']))
            else:
                # raise NotImplementedError(name)
                LOGGER.warning("not implemented: {}".format(name))

        return inputs

    def try_opendap(self, url):
        """Try to open the file as an OPeNDAP url and chunk it"""
        if url and not url.startswith("file"):
            r = requests.get(url + ".dds")
            if r.status_code == 200 and r.content.decode().startswith("Dataset"):
                ds = xr.open_dataset(url)
                chunks = chunk_dataset(ds, max_size=1000000)
                ds = ds.chunk(chunks)
                return ds

    def log_file_path(self):
        return os.path.join(self.workdir, 'log.txt')

    def sentry_configure_scope(self, request):
        """Add additional data to sentry error messages.

        When sentry is not initialized, this won't add any overhead.
        """
        with configure_scope() as scope:
            scope.set_extra("identifier", self.identifier)
            scope.set_extra("request_uuid", str(self.uuid))
            if request.http_request:
                # if the request has been put in the `stored_requests` table by pywps
                # the original request.http_request is not available anymore
                scope.set_extra("remote_addr", request.http_request.remote_addr)
                scope.set_extra("xml_request", request.http_request.data)

    def _handler(self, request, response):
        self.sentry_configure_scope(request)

        output_log_file = []

        def write_log(message, percentage=None):
            output_log_file.append(message)
            LOGGER.info(message)
            response.update_status(message, status_percentage=percentage)

        write_log("Processing started", 5)
        write_log("Preparing inputs", 5)
        kwds = {}
        LOGGER.debug("received inputs: " + ", ".join(request.inputs.keys()))
        for name, input_queue in request.inputs.items():
            input = input_queue[0]
            if isinstance(input, ComplexInput):
                ds = self.try_opendap(input.url)
                if ds:
                    write_log("Opened dataset as an OPeNDAP url: {}".format(input.url), 6)
                else:
                    write_log("Downloading dataset for url: {}".format(input.url), 6)
                    # accessing the file property downloads the file to disk
                    filename = input.file

                    ds = xr.open_dataset(filename)
                kwds[name] = ds.data_vars[name]

            elif isinstance(input, LiteralInput):
                kwds[name] = input.data

        write_log("Running computation", 10)
        LOGGER.debug("Calling xclim function with arguments: " + repr(kwds))
        out = self.xci(**kwds)
        out_fn = os.path.join(self.workdir, 'out.nc')

        write_log("Writing the output netcdf", 15)  # This should be the longest step
        out.to_netcdf(out_fn)

        write_log("Processing finished successfully", 98)

        response.outputs['output_netcdf'].file = out_fn
        response.outputs['output_log'].file = self.log_file_path()
        open(self.log_file_path(), "w").write("\n".join(output_log_file))

        return response


def chunk_dataset(ds, max_size=1000000):
    """Ensures the chunked size of a xarray.Dataset is below a certain size

    Cycle through the dimensions, divide the chunk size by 2 until criteria is met.
    """
    chunks = dict(ds.sizes)

    def chunk_size():
        return reduce(mul, chunks.values())

    for dim in cycle(chunks):
        if chunk_size() < max_size:
            break
        chunks[dim] = max(chunks[dim] // 2, 1)

    return chunks


def make_freq(name, default='YS', allowed=('YS', 'MS', 'QS-DEC', 'AS-JUL')):
    return LiteralInput(name, 'Frequency',
                        abstract='Resampling frequency',
                        data_type='string',
                        min_occurs=0,
                        max_occurs=1,
                        default=default,
                        allowed_values=allowed)


def make_thresh(name, default, abstract=''):
    return LiteralInput(name, 'threshold',
                        abstract=abstract,
                        data_type='float',
                        min_occurs=0,
                        max_occurs=1,
                        default=default,
                        )


def make_window(name, default, abstract=''):
    return LiteralInput(name, 'window',
                        abstract=abstract,
                        data_type='integer',
                        min_occurs=0,
                        max_occurs=1,
                        default=default,
                        )


def make_nc_input(name):
    return ComplexInput(name, 'Resource',
                        abstract='NetCDF Files or archive (tar/zip) containing netCDF files.',
                        metadata=[Metadata('Info')],
                        min_occurs=1,
                        max_occurs=1000,
                        supported_formats=[FORMATS.NETCDF])
