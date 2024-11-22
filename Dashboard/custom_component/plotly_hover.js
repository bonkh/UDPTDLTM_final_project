document.addEventListener("DOMContentLoaded", function () {
    // Get the Plotly div element by its ID
    const plotlyDiv = document.getElementById("plotly-graph");

    if (plotlyDiv) {
        // Listen to hover events on the Plotly chart
        plotlyDiv.on("plotly_hover", function (data) {
            const hoveredPoint = data.points[0];
            const hoverEvent = {
                eventType: "hover",
                pointNumber: hoveredPoint.pointNumber,
                label: hoveredPoint.label,
                insideTreemap: true  // Indicates hover is inside the treemap
            };

            // Send the event to Streamlit
            Streamlit.setComponentValue(hoverEvent);
        });

        // Listen to unhover events (when hover leaves the Treemap)
        plotlyDiv.on("plotly_unhover", function () {
            const unhoverEvent = {
                eventType: "unhover",
                insideTreemap: false  // Indicates hover is outside the treemap
            };

            // Send the event to Streamlit
            Streamlit.setComponentValue(unhoverEvent);
        });
    }
});
