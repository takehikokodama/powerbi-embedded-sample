import * as pbi from 'powerbi-client';

function init(config) {
    // Get models. models contains enums that can be used.
    // var models = window['powerbi-client'].models;
    var models = pbi.models;

    // We give All permissions to demonstrate switching between View and Edit mode and saving report.
    var permissions = models.Permissions.All;

    // Embed configuration used to describe the what and how to embed.
    // This object is used when calling powerbi.embed.
    // This also includes settings and options such as filters.
    // You can find more information at https://github.com/Microsoft/PowerBI-JavaScript/wiki/Embed-Configuration-Details.
    var powerbi_config= {
        type: 'report',
        tokenType: models.TokenType.Embed,
        accessToken: config.token,
        embedUrl: config.url,
        id: config.report_id,
        permissions: permissions,
        settings: {
            filterPaneEnabled: true,
            navContentPaneEnabled: true
        }
    };

    // Get a reference to the embedded report HTML element
    var reportContainer = document.getElementById('reportContainer');

    // Embed the report and display it within the div container.
    // var report = powerbi.embed(reportContainer, config);
    var powerbi = new pbi.service.Service(pbi.factories.hpmFactory, pbi.factories.wpmpFactory, pbi.factories.routerFactory);
    var report = powerbi.embed(reportContainer, powerbi_config);
}

window.init = init
