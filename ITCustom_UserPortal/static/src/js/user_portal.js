// Custom JS for User Portal Projects Page

odoo.define('ITCustom_UserPortal.user_portal', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.UserPortalProjects = publicWidget.Widget.extend({
        selector: '.custom-project-table',

        start: function () {
            this._super.apply(this, arguments);
            this._addAnimations();
            this._addTooltips();
        },

        _addAnimations: function () {
            // Add fade-in animation to project rows
            this.$('.project-row').each(function(index) {
                $(this).delay(100 * index).fadeIn(500);
            });
        },

        _addTooltips: function () {
            // Add tooltip to task count
            this.$('.task-count').tooltip({
                title: 'Number of tasks in this project',
                placement: 'top'
            });
        },
    });
});
