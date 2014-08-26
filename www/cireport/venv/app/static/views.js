
/**
 * Main application view.
 */
App.AppView = Backbone.View.extend({

    initialize: function (options) {
        App.debug('App.AppView.initialize()');
        this.options = options || {};
        this.CIModel = options.CIModel;

        _.bindAll(this, 'render');

        this.render();
    },



    render: function () {
        var self = this;

        App.debug('App.AppView.render()')
        self.chartView = new App.ChartView({ model: self.CIModel });
        self.$el.html('');
        App.debug(self.$el);


        this.$el.append(this.chartView.el);
        // }
        return this;
    }
})


App.ChartView = Backbone.View.extend({

    template: _.template($('#tpl-chart-view').html()),


    initialize: function (options) {
        App.debug('App.LoginView.initialize()');
        this.options = options || {};

        this.render();
    },

    events: {
    },

    StatsContainer : { text:''},
    TotalCount : { text: ''},
    createStats: function(viewContext,seriesData,xAxisCat){


$('#container2').highcharts({
            chart: {
                type: 'column'
            },


            // title: viewContext.StatsContainer,
            title: viewContext.TotalCount,
            // subtitle: viewContext.TotalCount,

            xAxis: {
                 categories: xAxisCat

            },

            yAxis: {
                min: 0,
                title: viewContext.totalPatchsets
            },

            tooltip: {
                headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                    '<td style="padding:0"><b>{point.y}</b></td></tr>',
                footerFormat: '</table>',
                shared: true,
                useHTML: true
            },

            plotOptions: {
                column: {
                    pointPadding: 0.2,
                    borderWidth: 0
                }
            },

            series: seriesData

        });
    },

    setupStats: function(viewContext, chart, e){
         setTimeout(function(){

                    self=chart;
                    viewContext.TotalCount['text'] = '';

                    nVisible=0;
                    for (var i = 0; i < self.series.length; i++) {
                        if(self.series[i].name == 'Total patchsets')
                        {
                            self.series[i].show();
                            patchset_sum = 0;
                           for(h=0;h<self.series[i].points.length;h++)
                            {
                             if(self.series[i].points[h].x>e.min && self.series[i].points[h].x < e.max)
                         {

                                patchset_sum = self.series[i].points[h].y+patchset_sum;
                            }
                        }
                        viewContext.TotalCount['text'] = "Total patchsets " + patchset_sum;
                        self.series[i].hide();
                        }
                        if (self.series[i].name == 'Navigator')
                        {
                            self.series.splice(i,1);
                            break;
                        }
                                    if (self.series[i].visible) {
                                        nVisible++;
                                    };
                    }

                    posValue = Array.apply(null, new Array(Math.floor((nVisible/3)))).map(Number.prototype.valueOf,-1);
                    negValue = Array.apply(null, new Array(Math.floor((nVisible/3)))).map(Number.prototype.valueOf,-1);
                    missValue = Array.apply(null, new Array(Math.floor((nVisible/3)))).map(Number.prototype.valueOf,-1);
                    totalValue = Array.apply(null, new Array(Math.floor((nVisible/3)))).map(Number.prototype.valueOf,-1);
                    xAxisCat = [];

                    for(j=0;j<self.series.length;j++)
                    {

                        sum=0;


                        if (self.series[j].visible)
                        {


                            ci_name = self.series[j].name.replace(' fail','').replace(' success','').replace(' missing','');

                            for(i=0;i<self.series[j].points.length;i++)
                            {

                            if(self.series[j].points[i].x>e.min && self.series[j].points[i].x < e.max)
                         {

                                sum = self.series[j].points[i].y+sum;
                            }
                            }

                            if(self.series[j].name.indexOf('success') > -1)
                            {
                                posValue[Math.floor(j/3)]=sum;
                            }
                            else
                                if(self.series[j].name.indexOf('fail') > -1)
                            {
                                negValue[Math.floor(j/3)]=sum;
                            }
                            else
                            {
                                 missValue[Math.floor(j/3)]=sum;
                            }

                            if (xAxisCat.indexOf(ci_name) < 0)
                                {

                                    xAxisCat.push(ci_name);
                                }
                        }
                    }


                    len1 = negValue.length> posValue.length?negValue.length:posValue.length;
                    len = len1 > missValue.length ? len1 : missValue.length;

                    for(i=0;i<len;i++){ if(posValue[i] == undefined) posValue[i]=-1;}
                    for(i=0;i<len;i++){ if(negValue[i] == undefined) negValue[i]=-1;}
                      for(i=0;i<len;i++){ if(missValue[i] == undefined) missValue[i]=-1;}

                    for (q=0;q<len;q++)
                    {
                        if(
                            (negValue[q]== -1 && posValue[q]== -1 && missValue[q]  == -1)
                            || (negValue[q]==undefined && posValue[q]== -1 && missValue[q] ==-1)
                            || (negValue[q]== -1  && missValue[q] == -1 && posValue[q]==undefined)
                            || (missValue[q]==undefined && posValue[q] == -1 && negValue[q] == -1)

                            || (missValue[q]==undefined && posValue[q] == undefined && negValue[q] == -1)
                            || (missValue[q]==undefined && posValue[q] == -1 && negValue[q] == undefined)
                            || (missValue[q]==-1 && posValue[q] == undefined && negValue[q] == -1)
                            )
                        {

                            negValue.splice(q,1);
                            posValue.splice(q,1);
                            missValue.splice(q,1);
                            q--;
                        }
                    }


                    ok=false;
                    for(i=0;i<posValue.length;i++){
                        if(posValue[i] != -1) {ok=true;
                            break;
                    }
                }
                    if(!ok)
                    {
                        posValue=[];
                    }
                    ok=false;
                    for(i=0;i<negValue.length;i++){
                     if(negValue[i] != -1){ok=true;break;}
                 }
                    if(!ok)
                    {
                        negValue=[];
                    }

                        ok=false;
                      for(i=0;i<missValue.length;i++){
                        if(missValue[i] != -1) {ok=true;break;}
                    }
                    if(!ok)
                    {
                        missValue=[];
                    }

                    for (i = 0; i< len;i++)
                    { sum =negValue[i] + posValue[i] + missValue[i] ;
                        if(! isNaN(sum) )
                    {

                        if(negValue[i]==-1)
                            sum+=1;
                        if(posValue[i]==-1)
                            sum+=1;
                        if(missValue[i]==-1)
                            sum+=1;
                        xAxisCat[i] += ' (Total ' + sum+ ' )';
                    }
                    }


                    seriesData = [
                    {name:'success', data:posValue, color:'#8CC610'},{name:'fail',data:negValue, color:'#BD008F' },{name:'missing',data:missValue, color:'#008EFF'}];

                    title_text =  'Stats for ' + Highcharts.dateFormat(null,e.min) + ' - ' + Highcharts.dateFormat(null,e.max);

                      $("#container").highcharts().setTitle({text:title_text});
                      // current = $('#head_title').html();
                      // if(current.indexOf('Stats') >0)
                      // {
                      //   new_title = current.replace(current.substring(current.indexOf('Stats')), text);
                      $('#stats_head').html(title_text);


                    viewContext.createStats(viewContext, seriesData, xAxisCat);



               },500);


    },
    createChart: function (viewContext, seriesOptions) {
        var self = this;
        $('#container').highcharts('StockChart', {
            chart: {
            },

            // title: viewContext.StatsContainer,

            navigator:{
                    enabled:false
            },

            rangeSelector: {
                selected: 0,
                   buttons:[
                            {
                                type: 'week',
                                count: 1,
                                text: '1w'
                            },
                            {
                                type: 'month',
                                count: 1,
                                text: '1m'
                            }, {
                                type: 'month',
                                count: 3,
                                text: '3m'
                            }, {
                                type: 'month',
                                count: 6,
                                text: '6m'
                            },
                            {
                                type: 'all',
                                text: 'All'
                            }
                    ]
            },

            xAxis: {
                       events: {
                 setExtremes: function(e) {

                    var self=this;
                    viewContext.setupStats(viewContext, self, e);

                }
            }
                    },
                     scrollbar: {
            liveRedraw: false

        },
            yAxis: {
                allowDecimals: false,
                plotLines: [{
                    value: 0,
                    width: 2,
                    color: 'silver'
                }]
            },
            plotOptions: {
                series: {
                    turboThreshold: 50000,
                    events:{
                        legendItemClick: function(event){
                            e = {min:$('#container').highcharts().xAxis[0].dataMin,max:$('#container').highcharts().xAxis[0].dataMax};
                                viewContext.setupStats(viewContext, $('#container').highcharts(), e);
                        }
                    },
                    dataGrouping : {
                            approximation: 'sum',
                            groupPixelWidth: 50,
                            units : [
                             [ 'hour',
                                    [1, 2, 3, 4, 6, 8, 12]
                            ],
                            ['day', [1]], ['week', [1]]
                            ]
                }
                }
            },
            chart:{
                zoomType: 'x'
            },
            legend: {
                    enabled: true,
            layout: 'vertical',
            align: 'left',
            verticalAlign: 'top',
            y: 100
            },
            tooltip: {
                pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> <br/>',
                valueDecimals: 0
            },

            series: seriesOptions
        },
        function(chart) {

            // apply the date pickers
            setTimeout(function() {
                $('input.highcharts-range-selector', $('#container')).datepicker()
            }, 50)
        }
        );
    },

    seriesOptions : [],

    render: function () {
        var self = this;

        App.debug('App.LoginView.render()');
        this.$el.html(this.template());
        var $el = self.$el;

        var novaB = $('#nova');
        novaB.click(function(){

        });

        $.when(self.model.load()).done(function(){

        x = self.model.toJSON();
        self.seriesOptions = [];

        len=x['CIs'].length;
        for (var i = 0;i<len; i++)
        {
        self.seriesOptions[i] = {

                                        name:x['CIs'][i]['_id'].replace("__positive"," success").replace("__negative"," fail").replace("__missing",' missing').replace("__exists",' patchsets'),
                                        data:x['CIs'][i]['patchsets']
    };

        }
        self.seriesOptions.sort(function(a,b){
            if(a['name'] < b['name'])
                return -1;
            if (a['name'] >b['name'])
                return 1;
            return 0;
        });

        len = self.seriesOptions.length;
        for (i=0;i< len; i++)
        {
            if(self.seriesOptions[i]['name'] == 'Total patchsets')
            {
                tmp = self.seriesOptions[i];
                self.seriesOptions[len] = tmp;
                self.seriesOptions.splice(i,1);
            }
        }

        color = ['#461B7E','#461B7E','#461B7E','#F75D59','#F75D59','#F75D59','#B5A642','#B5A642','#B5A642','#347C2C','#347C2C','#347C2C',
            '#F0563D','#F0563D','#F0563D',
            '#EFF1C2','#EFF1C2','#EFF1C2',
            '#B7C11E','#B7C11E','#B7C11E',
            '#23A38F','#23A38F','#23A38F',
            '#EAF1C2','#EAF1C2','#EAF1C2',
            ];

         for (var i = 0;i<len; i++)
        {

           self.seriesOptions[i]['color']=color[i];
           if((self.seriesOptions[i]['name'].indexOf('Jenkins') == 0 )
            ||(self.seriesOptions[i]['name'].indexOf('Hyper') == 0)
            ||(self.seriesOptions[i]['name'].indexOf('VMware') == 0)
            ){
           self.seriesOptions[i]['visible'] = true;
           }
           else
           {
            self.seriesOptions[i]['visible'] = false;
           }
            if(i%3==0)
            {
           self.seriesOptions[i]['dashStyle']='ShortDash';
            }
            if(i%3==1)
            {
            self.seriesOptions[i]['dashStyle'] = 'dot';
            }
         }
        self.createChart(self, self.seriesOptions);
        $.datepicker.setDefaults({
        dateFormat: 'yy-mm-dd',
        onSelect: function(dateText) {
        this.onchange();
            this.onblur();
            }
        });

        e = {min:$('#container').highcharts().xAxis[0].userMin,max:$('#container').highcharts().xAxis[0].userMax};
        self.setupStats(self, $('#container').highcharts(), e);
        $('#hide_all').click(function(){
            ser = $('#container').highcharts().series;

            // $.each(ser,function(index,series)
            // {
            //     console.log(index);
            //     if(series.visible == true){
            //         series.hide();
            //     }
            //     else
            //     {
            //         series.show();
            //     }
            // });
            // console.log(ser);
        });
        });
        return this;
    }

});

