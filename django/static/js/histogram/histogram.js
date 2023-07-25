/*
    SPDX-License-Identifier: AGPL-3.0-or-later
    Copyright (C) 2023 Divy Patel
*/

function renderHist(data, divId) {
    // Clear existing contents of the div
    d3.select("#" + divId).html("");

    // Set up dimensions and margins
    const margin = { top: 20, right: 30, bottom: 50, left: 50 };
    const width = 400 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    // Create SVG element with margins
    const svg = d3.select("#" + divId)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Create x and y scales
    const xScale = d3.scaleBand()
        .domain(data.values.map(d => d.label))
        .range([0, width])
        .padding(0.1);

    const yScale = d3.scaleLinear()
        .domain([0, d3.max(data.values, d => d.value)])
        .range([height, 0]);

    // Create new x and y scales for the top and right sides
    const xScaleTop = d3.scaleBand()
        .domain(data.values.map(d => d.label))
        .range([0, width])
        .padding(0.1);

    const yScaleRight = d3.scaleLinear()
        .domain([d3.max(data.values, d => d.value), 0])
        .range([0, height]);

    // Create x and y axes
    const xAxis = d3.axisBottom(xScale);
    const yAxis = d3.axisLeft(yScale);
    const xAxisTop = d3.axisTop(xScaleTop);
    const yAxisRight = d3.axisRight(yScaleRight);

    // Append x and y axes to the SVG
    svg.append("g")
        .attr("class", "axis-x")
        .attr("transform", `translate(0,${height})`)
        .call(xAxis);

    svg.append("g")
        .attr("class", "axis-y")
        .call(yAxis);

    // Append scondary x and y axes to the SVG for top and right sides
    svg.append("g")
        .attr("class", "axis-x-top")
        .call(xAxisTop);

    svg.append("g")
        .attr("class", "axis-y-right")
        .attr("transform", `translate(${width}, 0)`)
        .call(yAxisRight);

    // Create bars
    svg.selectAll("rect")
        .data(data.values)
        .enter()
        .append("rect")
        .attr("x", d => xScale(d.label))
        .attr("y", d => yScale(d.value))
        .attr("width", xScale.bandwidth())
        .attr("height", d => height - yScale(d.value))
        .attr("fill", "steelblue");

    // Add x-axis label
    svg.append("text")
        .attr("class", "axis-label")
        .attr("x", width / 2)
        .attr("y", height + margin.bottom - 10)
        .style("text-anchor", "middle")
        .text(data.xLabel);

    // Add y-axis label
    svg.append("text")
        .attr("class", "axis-label")
        .attr("transform", "rotate(-90)")
        .attr("x", -height / 2)
        .attr("y", -margin.left)
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text(data.yLabel);
}
