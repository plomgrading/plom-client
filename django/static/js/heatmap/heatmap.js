/*
    SPDX-License-Identifier: AGPL-3.0-or-later
    Copyright (C) 2023 Divy Patel
*/

function renderHeatMap(data, divId) {
    // Clear existing contents of the div
    d3.select("#" + divId).html("");

    // Set up dimensions and margins
    const cellSize = 40; // Set the desired cell size
    const margin = { top: 60, right: 50, bottom: 20, left: 60 };
    const width = data.cols * cellSize + margin.left + margin.right;
    const height = data.rows * cellSize + margin.top + margin.bottom;

    // Create the SVG container
    const svg = d3.select("#" + divId)
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    // Create a color scale
    const colorScale = d3.scaleSequential(d3.interpolateBlues)
        .domain([-1, 1]);

    // Create the heat map cells
    const cells = svg.selectAll("rect")
        .data(data.values.flat())
        .enter()
        .append("rect")
        .attr("x", (d, i) => (i % data.cols) * cellSize + margin.left) // Set the x-coordinate based on the column index
        .attr("y", (d, i) => Math.floor(i / data.cols) * cellSize + margin.top) // Set the y-coordinate based on the row index
        .attr("width", cellSize) // Set the desired cell width
        .attr("height", cellSize) // Set the desired cell height
        .attr("fill", d => colorScale(d)); // Set the cell color based on the value

    // Add x-axis labels at the top
    const xLabels = svg.selectAll(".xLabel")
        .data(data.xLabel)
        .enter()
        .append("text")
        .text(d => d)
        .attr("class", "xLabel")
        .attr("x", (d, i) => (i + 0.5) * cellSize + margin.left)
        .attr("y", margin.top * 2 / 3) // Adjust the y-coordinate to be at the top
        .style("text-anchor", "middle");

    // Add y-axis labels
    const yLabels = svg.selectAll(".yLabel")
        .data(data.yLabel)
        .enter()
        .append("text")
        .text(d => d)
        .attr("class", "yLabel")
        .attr("x", margin.left * 2 / 3)
        .attr("y", (d, i) => (i + 0.6) * cellSize + margin.top)
        .style("text-anchor", "middle");

    // Add x-axis title
    svg.append("text")
        .attr("class", "xTitle")
        .attr("x", width / 2)
        .attr("y", margin.top / 3) // Adjust the y-coordinate for the title
        .style("text-anchor", "middle")
        .text(data.xTitle);

    // Add y-axis title
    svg.append("text")
        .attr("class", "yTitle")
        .attr("transform", "rotate(-90)") // Rotate the text for vertical display
        .attr("x", -(margin.top + height) / 2)
        .attr("y", margin.left / 3) // Adjust the y-coordinate for the title
        .style("text-anchor", "middle")
        .text(data.yTitle);

    // Add color bar gradient
    const defs = svg.append("defs");
    const gradientId = "colorGradient";
    const gradient = defs.append("linearGradient")
        .attr("id", gradientId)
        .attr("x1", "0%")
        .attr("y1", "100%")
        .attr("x2", "0%")
        .attr("y2", "0%");

    gradient.selectAll("stop")
        .data(colorScale.ticks().map((tick, i, nodes) => ({
            offset: `${100 * i / (nodes.length - 1)}%`,
            color: colorScale(tick)
        })))
        .enter()
        .append("stop")
        .attr("offset", d => d.offset)
        .attr("stop-color", d => d.color);

    // Add color bar
    const colorBarWidth = 10;
    const colorBarHeight = height - margin.top - margin.bottom;
    const colorBar = svg.append("g")
        .attr("class", "colorBar")
        .attr("transform", `translate(${width - margin.right + 10}, ${margin.top})`);

    colorBar.append("rect")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", colorBarWidth)
        .attr("height", colorBarHeight)
        .attr("fill", `url(#${gradientId})`);

    const colorBarScale = d3.scaleLinear()
        .domain([-1, 1])
        .range([colorBarHeight, 0]);

    const colorBarAxis = d3.axisRight(colorBarScale)
        .ticks(5);

    // Append the axis to the colorBar group
    const colorBarAxisGroup = colorBar.append("g")
        .attr("class", "colorBarAxis")
        .call(colorBarAxis)
        .selectAll(".tick line")
        .attr("stroke", "#888") // Add style for tick lines
        .attr("stroke-dasharray", "2,2"); // Add style for dashed tick lines
}
