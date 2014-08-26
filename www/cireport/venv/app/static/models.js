
App.CIModel = Backbone.Model.extend({

    urlRoot: '/api/events',
    defaults: {
        id:'',
        CI: [],
        title: ''

    },


    loaded:false,

    afterSave: function (parser) {

                },

   load: function () {
            var self = this;
            var dfd = new $.Deferred();

            if (!self.loaded) {
                self.fetch({
                    success: function (model,response) {
                        self.loaded = true;
                        App.debug("Fetch model success");
                        self.afterSave(response);
                        // Return the Promise so caller can't change the Deferred
                        dfd.resolve(model, response);
                        // console.log(response);
                    },
                    error: function (model, response) {
                        self.loaded = false;
                        dfd.resolve(model,response);
                    }
                });
            }
            else {
                dfd.resolve();
            }

            return dfd.promise();
        },

    initialize: function () {
        App.debug('App.CIModel.initialize()');
    }
})
