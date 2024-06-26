import os
from datetime import datetime
import webbrowser
import tkinter as tk
from threading import Thread
import configparser

# Define the products
products = ["Builds", "DrakeBuilds"]

# Define the product families and their respective directories
federal_packages = ["C_Corporation", "Partnership", "S_Corporation", "Exempt", "Individual", "Estates_And_Trusts"]
states_abbr = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI"]

config_file = 'settings.ini'

# Define a function to check for "Build FAILED" in a file
def check_build_failed(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            if "Build FAILED" in content:
                return True
    except Exception as e:
        # Error reading file, do nothing
        pass
    return False

# Define a function to generate the HTML report
def generate_html_report(federal_builds, state_builds, year):
    report_time = datetime.now().strftime("%m-%d-%Y %I:%M %p")

    html_content = f"""
<html>
<head>
<title>{year} Compiler.err Report</title>
<script src="https://kryogenix.org/code/browser/sorttable/sorttable.js"></script>
</head>
<body>
<center><h1 style="margin-bottom:0">{year} Compiler.err Report</h1></center>
<center><h3 style="margin-top:0">Run Time: {report_time}</h3></center>
<p>
<hr style="height:3px;border-width:0;color:gray;background-color:gray">
<p>
<h2>Federal Builds</h2>
<table class="sortable" style="width:100%" border="1">
<tr>
<th width="7%" align="center">Product</th>
<th width="7%" align="center">Product Family</th>
<th width="10%" align="center">Package</th>
<th width="15%" align="center">Build</th>
<th width="7%" align="center">Status</th>
<th width="25%" align="center">Compiler.err File Path</th>
<th width="15%" align="center">Process.err</th>
<th width="22%" align="center">Timestamp</th>
</tr>"""

    for build in federal_builds:
        product, product_family, state, package, build_type, file_path, timestamp = build
        process_err_path = file_path.replace("compiler.err", "process.err")
        html_content += f"""
<tr>
<td align="center">{product}</td>
<td align="center">{product_family}</td>
<td align="center">{package}</td>
<td align="center">{build_type}</td>
<td align="center"><font color="red">BUILD FAILED</font></td>
<td align="center"><a href="{file_path}" target="_blank">{file_path}</a></td>
<td align="center"><a href="{process_err_path}" target="_blank">process.err</a></td>
<td align="center">{timestamp}</td>
</tr>"""

    html_content += """
</table>
<p>
<hr style="height:3px;border-width:0;color:gray;background-color:gray">
<p>
<h2>State Builds</h2>
<table class="sortable" style="width:100%" border="1">
<tr>
<th width="7%" align="center">Product</th>
<th width="7%" align="center">Product Family</th>
<th width="7%" align="center">State</th>
<th width="10%" align="center">Package</th>
<th width="15%" align="center">Build</th>
<th width="7%" align="center">Status</th>
<th width="25%" align="center">Compiler.err File Path</th>
<th width="15%" align="center">Process.err</th>
<th width="22%" align="center">Timestamp</th>
</tr>"""

    for build in state_builds:
        product, product_family, state, package, build_type, file_path, timestamp = build
        process_err_path = file_path.replace("compiler.err", "process.err")
        html_content += f"""
<tr>
<td align="center">{product}</td>
<td align="center">{product_family}</td>
<td align="center">{state}</td>
<td align="center">{package}</td>
<td align="center">{build_type}</td>
<td align="center"><font color="red">BUILD FAILED</font></td>
<td align="center"><a href="{file_path}" target="_blank">{file_path}</a></td>
<td align="center"><a href="{process_err_path}" target="_blank">process.err</a></td>
<td align="center">{timestamp}</td>
</tr>"""

    html_content += """
</table>
</body>
</html>"""

    output_file = "CompilerErrReport.html"
    with open(output_file, "w") as file:
        file.write(html_content)

    # Open the generated HTML file in the default web browser
    webbrowser.open(f"file://{os.path.abspath(output_file)}")

# Check each location for build failures
def check_builds(button, selected_federal, selected_states, year, selected_packages_list, env_var, build_var):
    button.config(text="Compiling...", state=tk.DISABLED, bg="blue")
    button.update_idletasks()

    base_path = rf"\\mhvfs01.taxact.com\Development\Tax{year}"

    federal_builds = []
    state_builds = []

    env = env_var.get()
    build = build_var.get()

    federal_build_types = [f"{env}_FEDMATH_{build}"]
    state_build_types = [f"{env}_{build}"]

    if selected_federal.get():
        for product in products:
            for package in selected_packages_list:
                for build_type in federal_build_types:
                    file_path = os.path.join(base_path, product, "Federal", package, build_type, "compiler.err")
                    if check_build_failed(file_path):
                        timestamp = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %I:%M:%S %p')
                        federal_builds.append((product, "Federal", "", package, build_type, file_path, timestamp))

    for state in states_abbr:
        if selected_states[state].get():
            for product in products:
                for package in selected_packages_list:
                    for build_type in state_build_types:
                        file_path = os.path.join(base_path, product, "States", state, package, build_type, "compiler.err")
                        if check_build_failed(file_path):
                            timestamp = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %I:%M:%S %p')
                            state_builds.append((product, "States", state, package, build_type, file_path, timestamp))

    # Sort state builds by state
    state_builds.sort(key=lambda x: x[2])

    # Generate the HTML report
    generate_html_report(federal_builds, state_builds, year)

    button.config(text="Generate Report", state=tk.NORMAL, bg="SystemButtonFace")
    button.update_idletasks()

    save_settings(year, selected_federal, selected_states, selected_packages_list, env_var, build_var)

def select_all_states(selected_states):
    for state_var in selected_states.values():
        state_var.set(True)

def unselect_all_states(selected_states):
    for state_var in selected_states.values():
        state_var.set(False)

def select_all_packages(selected_packages):
    for package_var in selected_packages.values():
        package_var.set(True)

def unselect_all_packages(selected_packages):
    for package_var in selected_packages.values():
        package_var.set(False)

def save_settings(year, selected_federal, selected_states, selected_packages_list, env_var, build_var):
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'Year': year, 'Federal': str(selected_federal.get()), 'Env': env_var.get(), 'Build': build_var.get()}
    config['States'] = {state: str(var.get()) for state, var in selected_states.items()}
    config['Packages'] = {package: str(package in selected_packages_list) for package in federal_packages}

    with open(config_file, 'w') as configfile:
        config.write(configfile)
    print("Settings saved.")

def load_settings():
    config = configparser.ConfigParser()
    if not os.path.exists(config_file):
        save_settings('2024', tk.BooleanVar(value=True), {state: tk.BooleanVar(value=True) for state in states_abbr}, federal_packages, tk.StringVar(value="DEV"), tk.StringVar(value="DEBUG"))

    config.read(config_file)

    year = config['DEFAULT'].get('Year', '2024')
    federal = config['DEFAULT'].getboolean('Federal', True)
    env = config['DEFAULT'].get('Env', 'DEV')
    build = config['DEFAULT'].get('Build', 'DEBUG')

    selected_states = {state: tk.BooleanVar(value=config['States'].getboolean(state, True)) for state in states_abbr}
    selected_packages = [package for package in federal_packages if config['Packages'].getboolean(package, True)]

    return year, federal, selected_states, selected_packages, env, build

def reset_defaults(year_entry, selected_federal, selected_states, selected_packages, env_var, build_var):
    year_entry.delete(0, tk.END)
    year_entry.insert(0, "2024")

    selected_federal.set(True)

    for state_var in selected_states.values():
        state_var.set(True)

    for package_var in selected_packages.values():
        package_var.set(True)

    env_var.set("DEV")
    build_var.set("DEBUG")

    save_settings("2024", selected_federal, selected_states, [package for package in federal_packages], env_var, build_var)
    print("Defaults reset and saved.")

def on_closing(root, year_entry, selected_federal, selected_states, selected_packages, env_var, build_var):
    save_settings(year_entry.get(), selected_federal, selected_states, [package for package, var in selected_packages.items() if var.get()], env_var, build_var)
    root.destroy()

# Define the main function to create the GUI
def main():
    root = tk.Tk()
    root.title("Compiler.err Report Generator")
    root.geometry("600x800")

    year, federal, selected_states, selected_packages_list, env, build = load_settings()

    selected_packages = {package: tk.BooleanVar(value=(package in selected_packages_list)) for package in federal_packages}

    label = tk.Label(root, text="Generate Compiler.err Report")
    label.pack(pady=5)

    year_frame = tk.Frame(root)
    year_frame.pack(pady=5)
    year_label = tk.Label(year_frame, text="Year:")
    year_label.pack(side=tk.LEFT)
    year_entry = tk.Entry(year_frame)
    year_entry.insert(0, year)
    year_entry.pack(side=tk.LEFT)

    # Create a frame for the environment radio buttons
    env_frame = tk.Frame(root)
    env_frame.pack(pady=5)
    env_var = tk.StringVar(value=env)
    tk.Radiobutton(env_frame, text="Dev", variable=env_var, value="DEV").pack(side=tk.LEFT)
    tk.Radiobutton(env_frame, text="Prod", variable=env_var, value="PROD").pack(side=tk.LEFT)

    # Create a frame for the build type radio buttons
    build_frame = tk.Frame(root)
    build_frame.pack(pady=5)
    build_var = tk.StringVar(value=build)
    tk.Radiobutton(build_frame, text="Debug", variable=build_var, value="DEBUG").pack(side=tk.LEFT)
    tk.Radiobutton(build_frame, text="Release", variable=build_var, value="RELEASE").pack(side=tk.LEFT)

    # Create a frame for the package checkboxes
    package_frame = tk.Frame(root)
    package_frame.pack(pady=5)

    package_label = tk.Label(package_frame, text="Packages:")
    package_label.grid(row=0, column=0, columnspan=2)

    for i, package in enumerate(federal_packages):
        package_checkbox = tk.Checkbutton(package_frame, text=package, variable=selected_packages[package])
        package_checkbox.grid(row=(i // 2) + 1, column=i % 2, sticky='w')

    select_all_packages_button = tk.Button(package_frame, text="Select All Packages", command=lambda: select_all_packages(selected_packages))
    select_all_packages_button.grid(row=len(federal_packages) // 2 + 2, column=0, pady=5)

    unselect_all_packages_button = tk.Button(package_frame, text="Unselect All Packages", command=lambda: unselect_all_packages(selected_packages))
    unselect_all_packages_button.grid(row=len(federal_packages) // 2 + 2, column=1, pady=5)

    # Create a frame for the federal checkbox
    federal_frame = tk.Frame(root)
    federal_frame.pack(pady=5)

    selected_federal = tk.BooleanVar(value=federal)
    federal_checkbox = tk.Checkbutton(federal_frame, text="Federal", variable=selected_federal)
    federal_checkbox.pack()

    # Create a frame for the state checkboxes
    state_frame = tk.Frame(root)
    state_frame.pack(pady=5)

    state_label = tk.Label(state_frame, text="States:")
    state_label.grid(row=0, column=0, columnspan=6)

    for i, state in enumerate(states_abbr):
        state_checkbox = tk.Checkbutton(state_frame, text=state, variable=selected_states[state])
        state_checkbox.grid(row=(i // 6) + 1, column=i % 6, sticky='w')

    # Create a frame for the state select/unselect buttons
    state_button_frame = tk.Frame(root)
    state_button_frame.pack(pady=5)

    select_all_states_button = tk.Button(state_button_frame, text="Select All States", command=lambda: select_all_states(selected_states))
    select_all_states_button.pack(side=tk.LEFT, padx=5)

    unselect_all_states_button = tk.Button(state_button_frame, text="Unselect All States", command=lambda: unselect_all_states(selected_states))
    unselect_all_states_button.pack(side=tk.LEFT, padx=5)

    generate_button = tk.Button(root, text="Generate Report", command=lambda: Thread(target=check_builds, args=(generate_button, selected_federal, selected_states, year_entry.get(), [package for package, var in selected_packages.items() if var.get()], env_var, build_var)).start())
    generate_button.pack(pady=5)

    reset_button = tk.Button(root, text="Reset to Defaults", command=lambda: reset_defaults(year_entry, selected_federal, selected_states, selected_packages, env_var, build_var))
    reset_button.pack(pady=5)

    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, year_entry, selected_federal, selected_states, selected_packages, env_var, build_var))

    root.mainloop()

# Run the main function
if __name__ == "__main__":
    main()
