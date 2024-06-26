import os
from datetime import datetime
import webbrowser
import tkinter as tk
from threading import Thread

# Define the products
products = ["Builds", "DrakeBuilds"]

# Define the product families and their respective directories
federal_packages = ["C_Corporation", "Partnership", "S_Corporation", "Exempt", "Individual", "Estates_And_Trusts"]
states_abbr = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI"]

# Define the build types for federal and states separately
federal_build_types = ["DEV_FEDMATH_DEBUG"]
state_build_types = ["DEV_DEBUG"]

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
def check_builds(button, selected_federal, selected_states, year, selected_packages):
    button.config(text="Compiling...", state=tk.DISABLED, bg="blue")
    button.update_idletasks()

    base_path = rf"\\mhvfs01.taxact.com\Development\Tax{year}"

    federal_builds = []
    state_builds = []

    if selected_federal.get():
        for product in products:
            for package in selected_packages:
                for build_type in federal_build_types:
                    file_path = os.path.join(base_path, product, "Federal", package, build_type, "compiler.err")
                    if check_build_failed(file_path):
                        timestamp = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %I:%M:%S %p')
                        federal_builds.append((product, "Federal", "", package, build_type, file_path, timestamp))

    for state in states_abbr:
        if selected_states[state].get():
            for product in products:
                for package in selected_packages:
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

# Define the main function to create the GUI
def main():
    root = tk.Tk()
    root.title("Compiler.err Report Generator")
    root.geometry("600x900")

    label = tk.Label(root, text="Generate Compiler.err Report")
    label.pack(pady=10)

    # Create a frame for the year input
    year_frame = tk.Frame(root)
    year_frame.pack(pady=10)
    
    year_label = tk.Label(year_frame, text="Year:")
    year_label.pack(side=tk.LEFT)
    
    year_entry = tk.Entry(year_frame)
    year_entry.insert(0, "2024")
    year_entry.pack(side=tk.LEFT)

    # Create a frame for the package selection
    package_frame = tk.Frame(root)
    package_frame.pack(pady=10)

    package_label = tk.Label(package_frame, text="Packages:")
    package_label.grid(row=0, column=0, columnspan=2)

    selected_packages = {}
    for i, package in enumerate(federal_packages):
        selected_packages[package] = tk.BooleanVar(value=True)
        package_checkbox = tk.Checkbutton(package_frame, text=package, variable=selected_packages[package])
        package_checkbox.grid(row=(i // 2) + 1, column=i % 2, sticky='w')

    select_all_packages_button = tk.Button(package_frame, text="Select All Packages", command=lambda: select_all_packages(selected_packages))
    select_all_packages_button.grid(row=len(federal_packages) // 2 + 2, column=0, pady=5)

    unselect_all_packages_button = tk.Button(package_frame, text="Unselect All Packages", command=lambda: unselect_all_packages(selected_packages))
    unselect_all_packages_button.grid(row=len(federal_packages) // 2 + 2, column=1, pady=5)

    # Create a frame for the federal checkbox
    federal_frame = tk.Frame(root)
    federal_frame.pack(pady=10)
    
    selected_federal = tk.BooleanVar(value=True)
    federal_checkbox = tk.Checkbutton(federal_frame, text="Federal", variable=selected_federal)
    federal_checkbox.pack()

    # Create a frame for the state checkboxes
    state_frame = tk.Frame(root)
    state_frame.pack(pady=10)
    
    state_label = tk.Label(state_frame, text="States:")
    state_label.grid(row=0, column=0, columnspan=5)

    selected_states = {}
    for i, state in enumerate(states_abbr):
        selected_states[state] = tk.BooleanVar(value=True)
        state_checkbox = tk.Checkbutton(state_frame, text=state, variable=selected_states[state])
        state_checkbox.grid(row=(i // 5) + 1, column=i % 5, sticky='w')

    # Create a frame for the state select/unselect buttons
    state_button_frame = tk.Frame(root)
    state_button_frame.pack(pady=10)

    select_all_states_button = tk.Button(state_button_frame, text="Select All States", command=lambda: select_all_states(selected_states))
    select_all_states_button.pack(side=tk.LEFT, padx=5)

    unselect_all_states_button = tk.Button(state_button_frame, text="Unselect All States", command=lambda: unselect_all_states(selected_states))
    unselect_all_states_button.pack(side=tk.LEFT, padx=5)

    generate_button = tk.Button(root, text="Generate Report", command=lambda: Thread(target=check_builds, args=(generate_button, selected_federal, selected_states, year_entry.get(), [package for package, var in selected_packages.items() if var.get()])).start())
    generate_button.pack(pady=20)

    root.mainloop()

# Run the main function
if __name__ == "__main__":
    main()
