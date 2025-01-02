import xarray as xr


class NetCDFMetaReader:
    def __init__(self, nc_path: str):
        self.nc_path = nc_path
        self._global_attrs = None
        self._variable_attrs = None

    def load(self) -> None:
        with xr.open_dataset(self.nc_path, decode_times=False) as ds:
            self._global_attrs = ds.attrs
            self._variable_attrs = dict()
            m = ds.variables.mapping
            for name, content in m.items():
                self._variable_attrs[name] = content.attrs


    @property
    def global_attrs(self) -> dict:
        if self._global_attrs is None:
            self.load()
        return self._global_attrs

    @property
    def variable_attrs(self):
        if self._variable_attrs is None:
            self.load()
        return self._variable_attrs
