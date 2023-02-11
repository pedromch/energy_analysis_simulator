from inputs import path_to_input, path_to_output_dir
from stream import Stream
from utils import range_is_subset, plot_great_composite_curve, plot_composite_curve
import pandas as pd
from os import path
from constants import ASSETS_FOLDER_NAME, INPUT_EXAMPLE_FILENAME

path_to_input = path_to_input if path_to_input is not None else path.abspath(path.join(path.dirname(path.dirname(__file__)), ASSETS_FOLDER_NAME, INPUT_EXAMPLE_FILENAME))
path_to_output_dir = path_to_output_dir if path_to_output_dir is not None else path.dirname(path_to_input)

def get_input(path_to_input):
    df = pd.read_excel(path_to_input)
    stream_list = [Stream(*row) for row in df.iloc[:, :4].itertuples(index=False)]
    min_approach = df.iloc[0, 4]
    return stream_list, min_approach

stream_list, min_approach = get_input(path_to_input)

hot_steps = []
cold_steps = []

for stream in stream_list:
    if stream.is_hot:
        hot_steps.extend([stream.Tin, stream.Tout])
        cold_steps.extend([stream.Tin - min_approach, stream.Tout - min_approach])
    else:
        cold_steps.extend([stream.Tin, stream.Tout])
        hot_steps.extend([stream.Tin + min_approach, stream.Tout + min_approach])

hot_steps = sorted(set(hot_steps), reverse=True)
cold_steps = sorted(set(cold_steps), reverse=True)

steps = [*zip(hot_steps, cold_steps)]

Q_liq = []
for i in range(len(steps) - 1):
    higher_hot, higher_cold = steps[i]
    lower_hot, lower_cold = steps[i + 1]

    temperature_step = higher_hot - lower_hot
    hot_range = [lower_hot, higher_hot]
    cold_range = [lower_cold, higher_cold]

    Q_step = 0
    for stream in stream_list:

        stream_range = stream.get_temperature_range()

        if stream.is_hot:
            if range_is_subset(hot_range, stream_range):
                Q_step += stream.mCp * temperature_step
        else:
            if range_is_subset(cold_range, stream_range):
                Q_step -= stream.mCp * temperature_step
        
    Q_liq.append(Q_step)


def get_Q_in_out(Q_liq, first_Q_in):
    out_list = [first_Q_in]
    for Q in Q_liq:
        out_list.append(out_list[-1] + Q)
    return out_list[:-1], out_list[1:]

first_Q_in = 0
Q_in_list = []
Q_out_list = []
while True:
    Q_in, Q_out = get_Q_in_out(Q_liq, first_Q_in)

    Q_in_list.append(Q_in)
    Q_out_list.append(Q_out)

    lower_Q_out = min(Q_out)
    if lower_Q_out < 0:
        first_Q_in -= lower_Q_out
    else:
        break

last_Q_in = Q_in_list[-1]
last_Q_out = Q_out_list[-1]

min_hot_utility = last_Q_in[0]
min_cold_utility = last_Q_out[-1]

for i in range(len(last_Q_in) - 1):
    if last_Q_in[i] == 0:
        pinch_index = i

pinch_hot, pinch_cold = steps[pinch_index]

NHE_without_pinch = len(stream_list) + 1 + 1 -1

def get_streams_above_and_bellow_pinch(pinch_hot, pinch_cold, stream_list):
    streams_above_pinch = []
    streams_bellow_pinch = []
    for stream in stream_list:
        if stream.is_hot:
            if stream.Tin > pinch_hot:
                streams_above_pinch.append(stream)
            if stream.Tout < pinch_hot:
                streams_bellow_pinch.append(stream)
        else:
            if stream.Tout > pinch_cold:
                streams_above_pinch.append(stream)
            if stream.Tin < pinch_cold:
                streams_bellow_pinch.append(stream)
    return streams_above_pinch, streams_bellow_pinch

above_number, bellow_number = map(len, get_streams_above_and_bellow_pinch(pinch_hot, pinch_cold, stream_list))

NHE_with_pinch = above_number + bellow_number

T_list_great_composite_curve = [(hot+cold)/2 for hot, cold in steps]
Q_list_great_composite_curve = Q_in_list[-1] + [min_cold_utility]

def get_composite_curve_data(steps_asc, streams):
    T_list = []
    Q_list = []
    i = 0
    while i < len(steps_asc) - 1:
        streams_in_interval = []
        first_T = steps_asc[i]
        j = i + 1
        while j < len(steps_asc):
            streams_in_step = []
            for stream in streams:
                stream_range = stream.get_temperature_range()
                if range_is_subset([steps_asc[i], steps_asc[j]], stream_range):
                    streams_in_step.append(stream)
            
            if streams_in_interval == [] and streams_in_step != []:
                streams_in_interval = streams_in_step
                last_T = steps_asc[j]
                i += 1
                j += 1
            elif streams_in_interval != [] and streams_in_interval == streams_in_step:
                last_T = steps_asc[j]
                i += 1
                j += 1
            elif streams_in_step == []:
                break
            elif streams_in_interval != [] and streams_in_interval != streams_in_step:
                break

        if streams_in_interval != []:
            if Q_list == []:
                T_list.append(first_T)
                Q_list.append(0)
            T_list.append(last_T)
            Q_list.append(Q_list[-1] + sum([stream.mCp * (last_T - first_T) for stream in streams_in_interval]))

        if streams_in_interval == []:
            i += 1

    return T_list, Q_list

hot_T, hot_Q = get_composite_curve_data(hot_steps[::-1], [stream for stream in stream_list if stream.is_hot])
cold_T, cold_Q = get_composite_curve_data(cold_steps[::-1], [stream for stream in stream_list if not stream.is_hot])
cold_Q = [Q + min_cold_utility for Q in cold_Q]

def get_energy_cascade_dataframe(steps, Q_liq, Q_in_list, Q_out_list):
    df = pd.DataFrame(columns=["HotInterval", "ColdInterval", "Qliq"])
    for i in range(len(Q_in_list)):
        df = pd.concat([df, pd.DataFrame(columns=[f"Qin{i + 1}", f"Qout{i + 1}"])])

    for i in range(len(steps) - 1):
        row_to_add = [f"{steps[i+1][0]}-{steps[i][0]}", f"{steps[i+1][1]}-{steps[i][1]}", Q_liq[i]]
        for Q_in, Q_out in zip(Q_in_list, Q_out_list):
            row_to_add.append(Q_in[i])
            row_to_add.append(Q_out[i])
        df.loc[i] = row_to_add
    return df

energy_cascade_dataframe = get_energy_cascade_dataframe(steps, Q_liq, Q_in_list, Q_out_list)

plot_great_composite_curve(T_list_great_composite_curve, Q_list_great_composite_curve, path_to_output_dir)
plot_composite_curve(hot_Q, hot_T, cold_Q, cold_T, path_to_output_dir)

with open(path.join(path_to_output_dir, "output.txt"), "w") as f:
    f.write("Results for the given streams")
    f.write(f"\n\nMin hot utility consumption: {min_hot_utility} kW")
    f.write(f"\nMin cold utility consumption: {min_cold_utility} kW")
    f.write(f"\nHot pinch: {pinch_hot} °C")
    f.write(f"\nCold pinch: {pinch_cold} °C")
    f.write(f"\nNHE without pinch: {NHE_without_pinch}")
    f.write(f"\nNHE with pinch: {NHE_with_pinch}")
    f.write("\n\nEnergy Cascade\n\n")
    f.write(energy_cascade_dataframe.to_string(index=False))
