var myChart = null; // Store chart instance globally

// Function to load and render chart based on type
function loadChart(chartType) {    
    if (!chartType) {
        // Clear chart if no type selected
        if (myChart) {
            myChart.destroy();
            myChart = null;
        }
        return;
    }
    
    $.ajax({
        url: "/trend_chart",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ chartType: chartType }),
        error: function() {
            alert("Error");
        },
        success: function(data, status, xhr) {
            
            if (data.chartType === 'amount') {
                renderAmountIncomingChart(data.chartDim);
            } else if (data.chartType === 'bookings') {
                renderBookingsByMonthChart(data.chartDim);
            }
        }
    });
}

// Render Amount Incoming Line Chart
function renderAmountIncomingChart(chartDim) {    
    var ctx = document.getElementById('myChart').getContext('2d');
    
    // Destroy existing chart
    if (myChart) {
        myChart.destroy();
    }
    
    var vLabels = []; // Hotel names
    var vData = [];   // Data points for each hotel
    
    // Process data from backend
    for (const [key, values] of Object.entries(chartDim)) {
        vLabels.push(key);
        let xy = [];
        for (let i = 0; i < values.length; i++) {
            let d = new Date(values[i][0]);
            let year = d.getFullYear();
            let month = ('' + (d.getMonth() + 1)).padStart(2, '0');
            let day = ('' + d.getDate()).padStart(2, '0');
            let aDateTime = year + '-' + month + '-' + day;
            xy.push({'x': aDateTime, 'y': values[i][1]});
        }
        vData.push(xy);
    }
        
    // Create chart
    myChart = new Chart(ctx, {
        data: {
        datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            
            scales: {
              x: {
                type: 'time',
                time: {
                  // "parser": "MM/DD/YYYY HH:mm",
                  parser: 'yyyy-MM-dd',
                },
                scaleLabel: {
                  display: true,
                  labelString: 'Date'
                }
              },
                y: {
                  scaleLabel: {
                    display: true,
                    labelString: 'value'
                  }
                }
            }
        }
    });
    
    // Add datasets for each hotel
    for (let i = 0; i < vLabels.length; i++) {
        myChart.data.datasets.push({
        label: vLabels[i],
        type: "line",
        borderColor: '#' + (0x1100000 + Math.random() * 0xffffff).toString(16).substr(1, 6),
        backgroundColor: "rgba(249, 238, 236, 0.74)",
        data: vData[i],
        spanGaps: true,
        });
    }
    myChart.update();
}

// Render Bookings By Month Bar Chart
function renderBookingsByMonthChart(chartDim) {
    var ctx = document.getElementById('myChart').getContext('2d');
    
    // Destroy existing chart
    if (myChart) {
        myChart.destroy();
    }
    
    // Extract all unique months across all hotels
    var allMonths = new Set();
    for (const [hotelName, monthCounts] of Object.entries(chartDim)) {
        monthCounts.forEach(([month, count]) => allMonths.add(month));
    }

    // Sort months chronologically
    var sortedMonths = Array.from(allMonths).sort((a, b) => new Date(a) - new Date(b));
    
    // Hotel names
    var hotelNames = Object.keys(chartDim);
    
    var datasets = [];
    var colorIndex = 0;

    // Build a dataset for each month
    for (const month of sortedMonths) {

        var colors = '#' + (0x1000000 + Math.random() * 0xFFFFFF).toString(16).substr(1,6);
    
        var dataPoints = hotelNames.map(hotelName => {
            // Find booking count for that month in that hotel
            var monthCounts = chartDim[hotelName];
            var found = monthCounts.find(([m, c]) => m === month);
            return found ? found[1] : 0;
        });

        datasets.push({
            label: month,
            data: dataPoints,
            backgroundColor: colors + '80',
            borderColor: colors,
            borderWidth: 1
        });

        colorIndex++;
    }

    // Create chart
    myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: hotelNames,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    ticks: {
                        autoSkip: false,
                        maxRotation: 45,
                        minRotation: 25
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Bookings'
                    },
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}


// Event listener for dropdown selection
$(document).ready(function() {
    $('#chartTypeSelect').on('change', function() {
        console.log('CHANGE EVENT FIRED!');
        var selectedValue = $(this).val();
        
        // Call the loadChart function
        loadChart(selectedValue);
    });
});