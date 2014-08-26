App.Router = Backbone.Router.extend({
    routes: {
        '': 'home'
        , '/': 'home'
        , 'nova': 'home'
        ,'neutron' :'neutron'
    },

    initialize: function (options) {
        App.debug('App.Router.initialize()');


    },
        home: function () {

        this.CIModel = new App.CIModel({id:'nova'});
        this.appView = new App.AppView({
            CIModel : this.CIModel
        });
        $('.content').html(this.appView.el);
    },


    neutron: function () {
        this.CIModel = new App.CIModel({id:'neutron'});
        this.appView = new App.AppView({
            CIModel : this.CIModel
        })
        $('.content').html(this.appView.el)
    },
    defaultRoute: function (routeId) {
        App.debug('Default route');
        console.log('Default route: ' + routeId);
    },

    _showPlaceholder: function (placeholder) {
        var self = this;
        $(placeholder).parent().children().hide();
        $(placeholder).show();
}
})
