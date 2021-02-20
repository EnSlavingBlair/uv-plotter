import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from astropy import units as u
from datetime import datetime, timedelta, date, time
from matplotlib import cm
from matplotlib.colors import ListedColormap
import re

### Plot UV Index over a year ###
# Read in each year on file of UV index
# Data taken from the Bureau of Meteorology for the Perth region

format_string = "%Y-%m-%d %H:%M:%S"

num_days = 366
num_mins = 1440
year = 2016

def get_year_dates(day_one, num_days):
    # create an array of dates starting at "day_one" and going for "num_days". Ignores the year
    day = date.fromisoformat(str(day_one))  # eg. day_one = '2020-01-01'
    date_list = np.array([str(day)]*num_days)
    day_delta = timedelta(days=1)
    for day_idx in range(num_days):
        date_list[day_idx] = str(day)
        day += day_delta
    return date_list

def get_24hr_minutes(day_min_one, num_mins):
    # create an array of minutes starting at "day_min_one", ignoring the input date, and going for "num_mins"
    dt = datetime.fromisoformat(day_min_one)  # eg. day_min_one = '2020-01-01 00:00:00'
    time_list = np.array([str(dt)]*num_mins)
    min_delta = timedelta(minutes=1)
    for min_idx in range(num_mins):
        time_list[min_idx] = str(dt.time())
        dt += min_delta
    return time_list

date_lines = []
uv_lines = []
with open("data/uv-perth-"+str(year)+".csv", "r") as f:
    # Read in the data from a CSV file and split lines into date and uv index level
    for line in f:
        line = re.split(',| ', line[:-1])
        date_lines.append(line[0]+" "+line[1])
        uv_lines.append(line[4])

# get 1D arrays of the required dates and times
date_list = get_year_dates('2020-01-01', num_days)  # no need to change year, it is ignored
time_list = get_24hr_minutes('2020-01-01 00:00:00', num_mins)  # no need to change date, it is ignored

# Create 2D array covering each plausible datetime combination of date_list and time_list
no_date = []
data = np.zeros([num_mins, num_days])
for date_idx in tqdm(range(len(date_list))):
    for min_idx in range(len(time_list)):
        try:
            datetime_elem = str(year)+date_list[date_idx][4:] + " " + time_list[min_idx]
            dt_idx = date_lines.index(datetime_elem)
            data[min_idx][date_idx] = uv_lines[dt_idx]
        except ValueError:
            no_date.append(datetime_elem)

plt.imshow(data)
plt.show()

# Set UV level ranges for low, moderate, high, very high and extreme
max_uv = np.max(data)
min_uv = np.min(data)
null = 0
low = int(np.floor(3/max_uv*256))
mod = int(np.floor(6/max_uv*256))
high = int(np.floor(8/max_uv*256))
vhigh = int(np.floor(11/max_uv*256))
ext = int(np.ceil(max_uv/max_uv*256))

# Set colours in colourbar
viridis = cm.get_cmap('viridis', 256)
newcolors = viridis(np.linspace(0, 1, 256))
null_grey = np.array([0.0, 0.0, 0.0, 0.5])
low_green = np.array([0.5647058823529412, 0.9333333333333333, 0.5647058823529412, 1])
mod_yellow = np.array([1.0, 1.0, 0.0, 1])
high_orange = np.array([1.0, 0.5490196078431373, 0.0, 1])
vhigh_red = np.array([1.0, 0.0, 0.0, 1])
ext_purple = np.array([0.7294117647058823, 0.3333333333333333, 0.8274509803921568, 1])
newcolors[:low, :] = low_green
newcolors[low:mod, :] = mod_yellow
newcolors[mod:high, :] = high_orange
newcolors[high:vhigh, :] = vhigh_red
newcolors[vhigh:, :] = ext_purple
newcolors[null, :] = null_grey
newcmp = ListedColormap(newcolors)

# Plot figure
hm = plt.imshow(data, cmap=newcmp)
plt.colorbar(hm)
plt.title(str(year))
plt.show()

# Save figure
hm = plt.imshow(data, cmap=newcmp)
plt.colorbar(hm)
plt.title(str(year))
plt.savefig("uv-perth"+str(year)+".png")
plt.clf()

# Save array to file so don't have to run computationally expensive analysis again
# np.savetxt("data/uv-perth-2019.txt", data_2019)

# TODO: Take