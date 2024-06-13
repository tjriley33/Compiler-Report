import os
from datetime import datetime
import webbrowser

# Define the base path
base_path = r"\\mhvfs01.taxact.com\Development\Tax2024"

# Define the products
products = ["Builds", "DrakeBuilds"]

# Define the product families and their respective directories
federal_packages = ["C_Corporation", "Partnership", "S_Corporation", "Exempt", "Individual", "Estates_And_Trusts"]
states_abbr = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

product_families = {
    "Federal": federal_packages,
    "States": states_abbr
}

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
        print(f"Error reading file {file_path}: {e}")
    return False

# Define a function to generate the HTML report
def generate_html_report(federal_builds, state_builds):
    report_time = datetime.now().strftime("%m-%d-%Y %I:%M %p (CST)")

    html_content = f"""
<html>
<head>
<title>2024 Compiler.err Report</title>
</head>
<body>
<center><h1 style="margin-bottom:0">2024 Compiler.err Report</h1></center>
<center><h3 style="margin-top:0">Run Time: {report_time}</h3></center>
<p>
<hr style="height:3px;border-width:0;color:gray;background-color:gray">
<p>
<h2>Federal Builds</h2>
<table style="width:100%" border="1">
<tr>
<th width="7%" align="center">Product</th>
<th width="7%" align="center">Product Family</th>
<th width="10%" align="center">Package</th>
<th width="15%" align="center">Build</th>
<th width="7%" align="center">Status</th>
<th width="54%" align="center">Compiler.err File Path</th>
</tr>"""

    for build in federal_builds:
        product, product_family, state, package, build_type, file_path = build
        html_content += f"""
<tr>
<td align="center">{product}</td>
<td align="center">{product_family}</td>
<td align="center">{package}</td>
<td align="center">{build_type}</td>
<td align="center"><font color="red">BUILD FAILED</font></td>
<td align="center"><a href="{file_path}" target="_blank">{file_path}</a></td>
</tr>"""

    html_content += """
</table>
<p>
<hr style="height:3px;border-width:0;color:gray;background-color:gray">
<p>
<h2>State Builds</h2>
<table style="width:100%" border="1">
<tr>
<th width="7%" align="center">Product</th>
<th width="7%" align="center">Product Family</th>
<th width="7%" align="center">State</th>
<th width="10%" align="center">Package</th>
<th width="15%" align="center">Build</th>
<th width="7%" align="center">Status</th>
<th width="54%" align="center">Compiler.err File Path</th>
</tr>"""

    for build in state_builds:
        product, product_family, state, package, build_type, file_path = build
        html_content += f"""
<tr>
<td align="center">{product}</td>
<td align="center">{product_family}</td>
<td align="center">{state}</td>
<td align="center">{package}</td>
<td align="center">{build_type}</td>
<td align="center"><font color="red">BUILD FAILED</font></td>
<td align="center"><a href="{file_path}" target="_blank">{file_path}</a></td>
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
federal_builds = []
state_builds = []

for product in products:
    for product_family, packages in product_families.items():
        if product_family == "Federal":
            for package in packages:
                for build_type in federal_build_types:
                    file_path = os.path.join(base_path, product, product_family, package, build_type, "compiler.err")
                    if check_build_failed(file_path):
                        federal_builds.append((product, product_family, "", package, build_type, file_path))
        elif product_family == "States":
            for state in packages:
                for package in federal_packages:
                    for build_type in state_build_types:
                        file_path = os.path.join(base_path, product, product_family, state, package, build_type, "compiler.err")
                        if check_build_failed(file_path):
                            state_builds.append((product, product_family, state, package, build_type, file_path))

# Sort state builds by state
state_builds.sort(key=lambda x: x[2])

# Generate the HTML report
generate_html_report(federal_builds, state_builds)
