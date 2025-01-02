import os
import xarray as xr


class BadFileTranslator:
    def __init__(self, nc_file_name, dataset_id, output):
        self.nc_file_name = nc_file_name
        self.output = output
        self.dataset_id = dataset_id

    def run(self):
        ds = xr.open_dataset(self.nc_file_name)
        df = ds.to_dataframe()
        df.to_xml(self.output)
        text = self.make_summary(df)
        summary_output_path = os.path.join(os.path.dirname(self.output), "{}_summary.txt".format(self.dataset_id))
        msg = "writing summary to {}".format(summary_output_path)
        print(msg)
        with open(summary_output_path, 'w') as f:
            f.write(text)

    def make_summary(self, df):
        summary = "Summary of {}\n\n{} nc file failed to load\n\n".format(self.dataset_id, len(df.index))

        txt = "{} nc files failed to load due to reason {}.\n"
        for pi, sub_dataset in df.groupby("reason"):
            summary += txt.format(len(sub_dataset.index), sub_dataset["reason"][0])
        return summary
