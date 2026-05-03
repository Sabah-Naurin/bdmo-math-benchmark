import os
import pandas as pd
from config import PROJECT_ROOT

# --- Configuration ---
CSV_FILE = os.path.join(PROJECT_ROOT, "evaluations", "chatgpt_results.csv")
HTML_FILE = os.path.join(PROJECT_ROOT, "evaluations", "interactive_report.html")

def create_interactive_html():
    print(f"Reading {CSV_FILE}...")
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print("CSV not found. Run your evaluation script first!")
        return

    # Convert DataFrame to basic HTML table
    table_html = df.to_html(index=False, classes="display", border=0, table_id="resultsTable")

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Math Benchmark Dashboard</title>
        
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
        
        <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
        
        <script>
        window.MathJax = {{
          tex: {{
            inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
            displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
          }}
        }};
        </script>
        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            h1 {{ color: #333; }}
            .MathJax {{ font-size: 1.1em; }} 
            
            /* Targeted dropdown styling */
            thead select {{
                width: 100%;
                margin-top: 5px;
                font-weight: normal;
                padding: 4px;
                box-sizing: border-box;
            }}
            
            /* Add some width to the text column so math formats nicely */
            td:nth-child(6) {{ min-width: 300px; }} 
        </style>
    </head>
    <body>
        <h1>Interactive Math Benchmark Dashboard</h1>
        <p>Use the dropdowns to filter specific attributes, or use the global search box. LaTeX is rendered natively.</p>
        
        {table_html}

        <script>
            $(document).ready(function () {{
                
                // 1. EXACT columns that should receive a dropdown
                var dropdownHeaders = ["Year", "Stage", "Region", "Category", "Has Image", "Status"];

                // 2. Inject dropdowns ONLY into the target columns
                $('#resultsTable thead th').each(function() {{
                    var title = $(this).text().trim();
                    if (dropdownHeaders.includes(title)) {{
                        $(this).append('<br><select class="column-filter"><option value="">All</option></select>');
                    }}
                }});

                // 3. Initialize DataTables
                var table = $('#resultsTable').DataTable({{
                    "pageLength": 25,
                    "drawCallback": function(settings) {{
                        if (window.MathJax && window.MathJax.typesetPromise) {{
                            MathJax.typesetClear([settings.nTBody]);
                            MathJax.typesetPromise([settings.nTBody]);
                        }}
                    }},
                    initComplete: function () {{
                        this.api().columns().every(function () {{
                            var column = this;
                            var headerText = $(column.header()).clone().children().remove().end().text().trim();
                            
                            // Only populate dropdown logic if this column is in our list
                            if (dropdownHeaders.includes(headerText)) {{
                                var select = $('select', this.header())
                                    .on('click', function(e) {{
                                        e.stopPropagation(); // Stop sorting when clicking dropdown
                                    }})
                                    .on('change', function () {{
                                        var val = $.fn.dataTable.util.escapeRegex($(this).val());
                                        column.search(val ? '^' + val + '$' : '', true, false).draw();
                                    }});

                                column.data().unique().sort().each(function (d, j) {{
                                    var text = $('<div>').html(d).text();
                                    select.append('<option value="' + text + '">' + text + '</option>');
                                }});
                            }}
                        }});
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    """

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_template)
        
    print(f"Interactive Dashboard generated: {HTML_FILE}")

if __name__ == "__main__":
    create_interactive_html()
