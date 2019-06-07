$(function(){
    var url = "http://127.0.0.1:8080/chat";
    var urlUsers = "http://127.0.0.1:8080/users";


    $("#grid").dxDataGrid({
        dataSource: DevExpress.data.AspNet.createStore({
            key: "id",
            loadUrl: url ,
            insertUrl: url ,
            updateUrl: url ,
            deleteUrl: url ,
            onBeforeSend: function(method, ajaxOptions) {
                ajaxOptions.xhrFields = { withCredentials: true };
            }
        }),
        editing: {
            allowUpdating: true,
            allowDeleting: true,
            allowAdding: true
        },
        remoteOperations: {
            sorting: true,
            paging: true
        },
        paging: {
            pageSize: 12
        },
        pager: {
            showPageSizeSelector: true,
            allowedPageSizes: [8, 12, 20]
        },
        columns: [{
            dataField: "id",
            dataType: "number",
            allowEditing: false
        }, {
            dataField: "content"
        }, {
            dataField: "sent_on",
            dataType: "datetime",
            allowEditing: false
        }, {
            dataField: "user_from_id",
            lookup: {
                dataSource: DevExpress.data.AspNet.createStore({
                    key: "id",
                    loadUrl: urlUsers ,
                    onBeforeSend: function(method, ajaxOptions) {
                        ajaxOptions.xhrFields = { withCredentials: true };
                    }
                }),
                displayExpr: "username",
                valueExpr: "id"
            }
        }, {
            dataField: "user_to_id",
            lookup: {
                dataSource: DevExpress.data.AspNet.createStore({
                    key: "id",
                    loadUrl: urlUsers,
                    onBeforeSend: function(method, ajaxOptions) {
                        ajaxOptions.xhrFields = { withCredentials: true };
                    }
                }),
                displayExpr: "username",
                valueExpr: "id"

            }
        },  ],
    }).dxDataGrid("instance");
});
