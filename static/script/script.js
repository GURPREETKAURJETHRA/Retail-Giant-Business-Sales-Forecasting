// google.charts.load('45.2', {'packages':['corechart']});
// google.charts.setOnLoadCallback(DrawChart);

function AddStores()
{
    var list = document.getElementById("store-selection-list");
    for (i = 2; i <= 1115; i++)
    {
        var option = document.createElement("option");
        option.text = i;
        option.value = i;
        list.appendChild(option); 
    }
}

function SetDefaultDate()
{
    var date = new Date();
    var current_date  = date.getFullYear().toString() + '-' + (date.getMonth() + 1).toString().padStart(2, '0') + '-' +date.getDate().toString().padStart(2, '0');
    
    var collection = document.getElementsByClassName("datepicker");
    for (let i = 0; i < collection.length; i++) {
        collection[i].value = current_date;
    }
}

function ToggleSalesIndicatorsVisibility(display)
{
    if (typeof(display) == typeof(true))
    {
        var sales_collection = document.getElementsByClassName("sales-indicator");
        var do_display = display ? 'block' : 'none';
    
        for (let i = 0;i < sales_collection.length; i++) {
            sales_collection[i].style.display = do_display;
        }
    }
    else
    {
        console.log("The argument is not a boolean value. Datatype: ", typeof(display));
    }
}

// function ToggleVisualizationVisibility(display)
// {
//     if (typeof(display) == typeof(true))
//     {
//         var visualization = document.getElementById("curve-chart");
//         var do_display = display ? 'block' : 'none';
    
//         visualization.style.display = do_display
//     }
//     else
//     {
//         console.log("The argument is not a boolean value. Datatype: ", typeof(display));
//     }
// }

function ToggleResultsVisibility(display)
{
    ToggleSalesIndicatorsVisibility(display)
    // ToggleVisualizationVisibility(display)
}

function ChangeToDateMinValue()
{
    var from_date_element = document.getElementById("from-date-selector-input");
    var to_date_element = document.getElementById("to-date-selector-input");

    to_date_element.min = from_date_element.value;
    if (from_date_element.value > to_date_element.value)
    {
        to_date_element.value = to_date_element.min;
    }

    // ToggleResultsVisibility(false)
}

function ChangeFromDateMaxValue()
{
    var from_date_element = document.getElementById("from-date-selector-input");
    var to_date_element = document.getElementById("to-date-selector-input");

    from_date_element.max = to_date_element.value;
    if (from_date_element.value > to_date_element.value)
    {
        from_date_element.value = to_date_element.value
    }

    // ToggleResultsVisibility(false)
}

function ChangeButtonColor()
{
    document.getElementById('predict-button').style.backgroundColor = '#ffffff';
    document.getElementById('predict-button').style.color = '#c91f20';
}

function RevertButtonColor()
{
    document.getElementById('predict-button').style.backgroundColor = '#c91f20';
    document.getElementById('predict-button').style.color = '#ffffff';
}

// function DrawChart(data) 
// {
//     var data = google.visualization.arrayToDataTable(data);

//     var options = {
//         curveType: 'function',
//         legend: 'none',
//         series: {0: { color: '#c91f20' }},
//         backgroundColor: {'fill': '#00FFFFFF'},
//         width: 500,
//         height: 180,
//         chartArea:{left:5, top:15, right: 5, bottom: 15, width:'100%', height: '100%'},
//         vAxis:{textPosition: 'in'}
//     };

//     var chart = new google.visualization.LineChart(document.getElementById('curve-chart'));
//     chart.draw(data, options);
// }

// function DisplaySales(data)
// {
//     var sumOfSales = 0

//     for (let i = 0; i < data.length; i++)
//     {
//         sumOfSales += Math.round(data[i][1])
//     }

//     console.log("Data: ", data);
//     console.log("Sum: ", sumOfSales.toLocaleString("en-US"))
//     console.log("Avg: ", Math.round(sumOfSales / data.length).toLocaleString("en-US"))
    
//     document.getElementById('total-sales-indicator').innerHTML = "$ " + Math.round(sumOfSales).toLocaleString("en-US")
//     document.getElementById('avg-sales-indicator').innerHTML = "$ " + Math.round(sumOfSales / data.length).toLocaleString("en-US")

//     data.unshift(['Date', 'Sales'])
//     console.log(data);
//     // DrawChart(data)
// }

// function SendValuesToApi()
// {
//     var store_id = document.getElementById("store-selection-list").value;
//     var from_date = document.getElementById("from-date-selector-input").value;
//     var to_date = document.getElementById("to-date-selector-input").value;

//     const data = {"data": 
//     {
//         "store": store_id,
//         "from_date": from_date,
//         "to_date": to_date
//     }}
//     api_url = 'http://127.0.0.1:5500/predict_api'

//     fetch(api_url, {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify(data)
//     })
//     .then(response => { if (response.ok) { return response.json(); } else { throw new Error('Something went wrong'); }})
//     .then(data => { DisplaySales(data); })
//     .catch(error => { console.error(error); });
// }

function PredictSales()
{
    document.getElementById('total-sales-indicator').innerHTML = "Calculating..."
    document.getElementById('avg-sales-indicator').innerHTML = "Calculating..."

    ToggleResultsVisibility(true);
    // SendValuesToApi();
}

function SiteLoading()
{
    AddStores();
    SetDefaultDate();
    // ToggleResultsVisibility(false)
}

window.onload = SiteLoading();