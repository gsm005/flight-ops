const baseUrl = "https://www.flightstats.com/v2";
const trackUrlTemplate = `${baseUrl}/api-next/flick/%%flightId%%?guid=34b64945a69b9cac:5ae30721:13ca699d305:XXXX&airline=%%airline%%&flight=%%flight%%&flightPlan=true&rqid=xd2cssu74sf`;

// Function to get flight details
async function getDetails(flightId, airline, flight) {
    const url = trackUrlTemplate
        .replace("%%flightId%%", flightId)
        .replace("%%airline%%", airline)
        .replace("%%flight%%", flight);

    const response = await fetch(url);
    const responseJson = await response.json();
    return responseJson;
}

async function getFlightId(airline, flight) {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0'); // Months are 0-based
    const date = String(now.getDate()).padStart(2, '0');

    const url = `${baseUrl}/flight-tracker/${airline}/${flight}?year=${year}&month=${month}&date=${date}`;
    const response = await fetch(url);
    const responseText = await response.text();

    const match = responseText.match(/flightId=(\d+)/);
    return match ? match[1] : null;
}

async function getFlightDetails(flightcode = "6E17") {
    const airline = flightcode.slice(0, 2);
    const flight = flightcode.slice(2);

    const flightId = await getFlightId(airline, flight);
    if (flightId) {
        const data = await getDetails(flightId, airline, flight);
        data.success = true;
        return data;
    } else {
        return { success: true, message: "Flight ID not found" };
    }
}

console.log(window.href);
getFlightDetails("6E17").then(data => console.log(data));
