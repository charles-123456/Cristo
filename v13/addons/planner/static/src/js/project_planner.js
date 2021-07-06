odoo.define('planner.PlannerAnalysis', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var core = require('web.core');
var rpc = require('web.rpc');
var session = require('web.session');
var web_client = require('web.web_client');
var _t = core._t;
var QWeb = core.qweb;

var PlannerDashboard = AbstractAction.extend({
    template: 'ProjectPlanMain',
    cssLibs: [
	],
	jsLibs: [
	],
    events: {
    },

    init: function(parent, action, context) {
    	this._super.apply(this, arguments);
        this.plan_id = action.context.active_id || action.params.active_id;
    },

    start: function() {
        var self = this;
        this.set("title", 'Plan Analysis');
        this._rpc({
            model: 'project.plan',
            method: 'get_plan_analysis_details',
            args: [[self.plan_id]],
        })
        .then(function(result) {
        	self.plan_data = result[0];
//        	console.log(self.plan_data)
        	self.$el.html(QWeb.render('ProjectPlanMain', {widget:self.plan_data}));
        	if(result[0]['sec1_data']){
        		self.sec1_Data(result[0]['sec1_data']);
        	}
//        	self.actType_Data(result[0]['act_type_data']);
        	self.activityChart(result[0]['act_data']);
        });
        return self._super.apply(this, arguments);
    },
    
    /*fetch_data: function() {
        var self = this;
        var def1 =  this._rpc({
                model: 'res.member',
                method: 'get_user_member_details'
        }).then(function(result) {
            self.login_member =  result[0];
        });
        var def2 =  this._rpc({
            model: 'res.member',
            method: 'get_member_statistics'
        }).then(function(data) {
        	self.mem_statistics = data;
        });
        return $.when(def1,def2);
    },*/
    getRandomColor : function() {
    	return "#" + Math.random().toString(16).slice(2,8);
    },
    sec1_Data : function(data){
//    	console.log(data);
    	var self = this;
    	var main_data = [];
    	_.each(data[0]['overall'], function(dt){
    		var color = self.getRandomColor();
	    	var common_data = {
	    	          label               : dt['label'],
	    	          backgroundColor     : color,
	    	          borderColor         : color,
	    	          pointRadius          : true,
	    	          pointColor          : color,
	    	          pointStrokeColor    : color,
	    	          pointHighlightFill  : '#fff',
	    	          data                : dt['data_set']
	    	        }
	    	main_data.push(common_data);
    	});
    	var barChartCanvas = this.$('#sec1Chart').get(0).getContext('2d');
        var barData        = {
          labels: data[0]['labels'],
          datasets: main_data
        }
    	var barOptions     = {
    	      maintainAspectRatio : false,
    	      responsive : true,
    	      datasetFill: false,
    	    }
    	var donutChart = new Chart(barChartCanvas, {
	      type: 'bar',
	      data: barData,
	      options: barOptions
	    });
    },
    activityChart : function(data){
    	var self = this;
    	var labels = [];
    	var values = [];
    	_.each(data, function(dt){
            labels.push(dt['state']);
            values.push(dt['state_count']);
        });
    	var donutChartCanvas = this.$('#activityChart').get(0).getContext('2d');
        var donutData        = {
          labels: labels,
          datasets: [
            {
              data: values,
              backgroundColor : ['#f56954', '#00a65a', '#f39c12'],
            }
          ]
        }
    	var donutOptions     = {
    	      maintainAspectRatio : false,
    	      responsive : true,
    	    }
        //Create pie or douhnut chart
        // You can switch between pie and douhnut using the method below.
    	var donutChart = new Chart(donutChartCanvas, {
	      type: 'doughnut',
	      data: donutData,
	      options: donutOptions
	    });
    },
    /*destroy: function () {
        clearTimeout(this.return_to_main_menu);
        this._super.apply(this, arguments);
    },
    */
        
});


core.action_registry.add('plan_analysis_view', PlannerDashboard);

return PlannerDashboard;

});
