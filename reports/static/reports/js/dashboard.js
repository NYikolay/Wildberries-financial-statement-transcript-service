const graphWrapper = document.getElementById("graphs-bar-wrap")
const graphDiogWrapper = document.getElementById("graphs-diog-wrap")
const brandShareInRevenueData = JSON.parse(graphDiogWrapper.getAttribute("data-brands-share"))
const stockShareInRevenueData = JSON.parse(graphDiogWrapper.getAttribute("data-stock-share"))
const reportByWeekData = JSON.parse(graphWrapper.getAttribute('data-report'))
const changeReportInput = document.getElementById('change-report')

let bars_x = 0;
let bars_x_offset = 0;

let bars_y = 0;
let bars_y_offset = document.querySelector('.graphs-bar__info-add').offsetHeight;

function createBar(data_bar) {

	// Блоки с контентом
	let bar_div_revenue = document.querySelector('.graphs-bar__revenue');
	let bar_div_profit = document.querySelector('.graphs-bar__profit');

	let bar_div_count = document.querySelector('.graphs-bar__count');

	// Количество блоков
	let bar_count = data_bar.length;

	// Получение максимальной высоту графика
	let bar_max_height = document.querySelector('.graphs-bar__profit-item-check').clientHeight;


	bar_div_revenue.innerHTML = '';


	let bar_pb_el = document.querySelector('.graphs-bar__bars');
	let bar_pb = window.getComputedStyle(bar_pb_el, null).getPropertyValue("padding-bottom");



	let bar_revenue_min = 0;
	let bar_revenue_max = 0;

	let bar_profit_min = 0;
	let bar_profit_max = 0;

	for (var i = 0; i < bar_count; i++) {

		if (data_bar[i]['revenue'] > bar_revenue_max) {
			bar_revenue_max = data_bar[i]['revenue'];
		}

		if (data_bar[i]['revenue'] < bar_revenue_min) {
			bar_revenue_min = data_bar[i]['revenue'];
		}

		if (data_bar[i]['profit'] > bar_profit_max) {
			bar_profit_max = data_bar[i]['profit'];
		}

		if (data_bar[i]['profit'] < bar_profit_min) {
			bar_profit_min = data_bar[i]['profit'];
		}
	}

	let bar_max_value = bar_revenue_max;
	if (bar_profit_min < 0) {
		bar_max_value = bar_max_value + (-1 * bar_profit_min);
	}

	let bar_revenue_percent = bar_max_height / bar_max_value;

	// Добавить отсуп снизу, если есть отрицальное значение
	if (bar_profit_min < 0) {
		height = bar_revenue_percent * bar_profit_min * -1;
		value = String(height) +'px + '+ bar_pb;

		bar_pb_el.style.paddingBottom = 'calc('+value+')';
		bar_div_profit.style.bottom = 'calc('+value+')';

		bars_y = Number(height) + Number(bar_pb.slice(0, -2));

	}

	bar_div_count.innerHTML = '';

	for (var i = 0; i < bar_count; i++) {

		addsLeftRight = '';
		if ((i == 0) || (i == 1)) {
			addsLeftRight = 'data-position="left"';
		} else if ((i == (bar_count-1)) || (i == bar_count-2)) {
			addsLeftRight = 'data-position="right"';
		}

		attrs = 'data-date_from="'+data_bar[i]['date_from']+'" ' +'data-date_to="'+data_bar[i]['date_to']+'" ' +'data-week_num="'+data_bar[i]['week_num']+'" ' +'data-revenue="'+Math.round(data_bar[i]['revenue']).toLocaleString()+'" ' +'data-sales_amount="'+Math.round(data_bar[i]['sales_amount']).toLocaleString()+'" ' +'data-returns_amount="'+Math.round(data_bar[i]['returns_amount']).toLocaleString()+'" ' +'data-logistics="'+Math.round(data_bar[i]['logistics']).toLocaleString()+'" ' +'data-net_costs_sum="'+Math.round(data_bar[i]['net_costs_sum']).toLocaleString()+'" ' +'data-marginality="'+Math.round(data_bar[i]['marginality']).toLocaleString()+'" ' +'data-commission="'+Math.round(data_bar[i]['commission']).toLocaleString()+'" ' +'data-supplier_costs="'+Math.round(data_bar[i]['supplier_costs']).toLocaleString()+'" ' +'data-wb_costs="'+Math.round(data_bar[i]['wb_costs']).toLocaleString()+'" ' +'data-tax="'+Math.round(data_bar[i]['tax']).toLocaleString()+'" ' +'data-profit="'+Math.round(data_bar[i]['profit']).toLocaleString()+'" ' +'data-profitability="'+Math.round(data_bar[i]['profitability']).toLocaleString()+'" ';

		current_revenue_percent = data_bar[i]['revenue'] * bar_revenue_percent;
		bar_div_revenue.innerHTML += '<div '+addsLeftRight+' '+attrs+' class="graphs-bar__revenue-item" style="height: ' + current_revenue_percent + 'px"></div>';


		if (data_bar[i]['profit'] >= 0) {
			current_profit_percent = data_bar[i]['profit'] * bar_revenue_percent;
			bar_div_profit.innerHTML += '<div '+addsLeftRight+' '+attrs+' class="graphs-bar__profit-item" style="height: ' + current_profit_percent + 'px"></div>';
		} else {
			current_profit_percent = data_bar[i]['profit'] * bar_revenue_percent * -1;
			bar_div_profit.innerHTML += '<div '+addsLeftRight+' '+attrs+' class="graphs-bar__profit-item border-radius-bottom" style="height: ' + current_profit_percent + 'px; transform: translateY('+current_profit_percent+'px)"></div>';
		}
		//bar_info.style.bottom = '' + String(bars_y-(bars_y_offset/2)) + 'px';


		bar_div_count.innerHTML += '<span class="graphs-bar__count-item">'+data_bar[i]['week_num']+'</span>';
	}


	// Уменьшить блоки, содержащие данные о текущей неделе
	current_bar_width = document.querySelector('.graphs-bar__profit-item').getBoundingClientRect().width;
	current_num_width = document.querySelector('.graphs-bar__count-item').getBoundingClientRect().width;

	if (current_bar_width != current_num_width) {
		elements = document.getElementsByClassName('graphs-bar__count-item');

		for (var i = 0; i < elements.length; i++) {
			elements[i].classList.add('graphs-bar__count-item-min');

		}

		document.querySelector('.graphs-bar__legend-item').classList.add('graphs-bar__legend-item-min');

	}


	showBarInfo();

}

// Открытие подсказки
// let bar_tooltip = document.querySelector('.graphs-bar__tooltip-info');
// let bar_tooltip_btn = document.querySelector('.graphs-bar__tooltip-btn');
//
// bar_tooltip_btn.addEventListener('mouseover', function() {
// 	bar_tooltip.classList.add('showed');
// });
//
// bar_tooltip_btn.addEventListener('mouseleave', function() {
// 	bar_tooltip.classList.remove('showed');
// });

/*document.addEventListener('click', function(e) {
	target = e.target.classList;

	if (target.contains('graphs-bar__tooltip-btn') || target.contains('graphs-bar__tooltip-info')) {
		if (target.contains('graphs-bar__tooltip-btn')) {
			if (bar_tooltip.classList.contains('showed')) {
				bar_tooltip.classList.remove('showed');
			} else {
				bar_tooltip.classList.add('showed');
			}
		} else {
			bar_tooltip.classList.add('showed');
		}

	} else {
		bar_tooltip.classList.remove('showed');
	}
});*/


/*document.addEventListener('mouseover', function(e) {
	target = e.target.classList;

	if (target.contains('graphs-bar__tooltip-btn') || target.contains('graphs-bar__tooltip-info')) {
		if (target.contains('graphs-bar__tooltip-btn')) {
			if (bar_tooltip.classList.contains('showed')) {
				bar_tooltip.classList.remove('showed');
			} else {
				bar_tooltip.classList.add('showed');
			}
		} else {
			bar_tooltip.classList.add('showed');
		}

	} else {
		bar_tooltip.classList.remove('showed');
	}
});*/



/*bars_profit[i].addEventListener('mouseleave', function() {
			bar_info.classList.remove('showed');
		});*/


// Логика работы всплывающего окна с информацией

let bar_info = document.querySelector('.graphs-bar__info');

let screen_width = window.innerWidth;

if (screen_width <= 480) {
	bar_info.classList.add('graphs-bar__info-480px');
} else if (screen_width <= 768) {
	bar_info.classList.add('graphs-bar__info-768px');
}

function showBarInfo() {

	var bars_profit = document.getElementsByClassName('graphs-bar__profit-item');
	var bars_revenue = document.getElementsByClassName('graphs-bar__revenue-item');

	let bars_info_title = document.querySelector('.graphs-bar__info-title');
	let bars_info_span = document.getElementsByClassName('graphs-bar__info-span');

	let bars_add = document.querySelector('.graphs-bar__info-add');

	for(var i = 0; i < bars_profit.length; i++) {
		bars_profit[i].addEventListener('mouseover', function(e) {

			result = [];
			result.push(this.getAttribute('data-date_from'));
			result.push(this.getAttribute('data-date_to'));
			result.push(this.getAttribute('data-week_num'));
			result.push(this.getAttribute('data-revenue'));
			result.push(this.getAttribute('data-sales_amount'));
			result.push(this.getAttribute('data-returns_amount'));
			result.push(this.getAttribute('data-logistics'));
			result.push(this.getAttribute('data-net_costs_sum'));
			result.push(this.getAttribute('data-marginality'));
			result.push(this.getAttribute('data-commission'));
			result.push(this.getAttribute('data-supplier_costs'));
			result.push(this.getAttribute('data-wb_costs'));
			result.push(this.getAttribute('data-tax'));
			result.push(this.getAttribute('data-profit'));
			result.push(this.getAttribute('data-profitability'));

			bars_info_title.textContent = result[0] + ' - ' + result[1];

			bars_info_span[0].textContent = result[13];
			bars_info_span[1].textContent = result[8] + ' %';
			bars_info_span[2].textContent = result[14] + ' %';
			bars_info_span[3].textContent = result[4];
			bars_info_span[4].textContent = result[5];
			bars_info_span[5].textContent = result[3];
			bars_info_span[6].textContent = result[7];
			bars_info_span[7].textContent = result[9];
			bars_info_span[8].textContent = result[6];
			bars_info_span[9].textContent = result[11];
			bars_info_span[10].textContent = result[10];
			bars_info_span[11].textContent = result[12];


			/*if (screen_width <= 480) {
				bar_info.style.bottom = '' + String(-1*(bars_y-(bars_y_offset/2)) +10) + 'px';

				bars_x = this.offsetLeft + (this.getBoundingClientRect().width / 2);

				bars_add.style.left = '' + bars_x +'px';


			} else if (screen_width <= 768) {

				bars_x = this.offsetLeft + (this.getBoundingClientRect().width / 2);
				bar_info.style.left = '' + bars_x +'px';

				position = this.getAttribute('data-position');
				if (position == 'left') {
					bar_info.style.left = 0;

					bar_info.classList.add('left768px');
					bars_add.style.left = '' + bars_x +'px';

					bars_add.style.transform = 'translateX(-50%)';

				} else if (position == 'right') {
					bar_info.style.left = 'auto';
					bar_info.style.right = '0';

					bar_info.classList.add('right768px');
					bars_add.style.left = 'auto';


					bars_x = this.offsetLeft;

					max_width_temp = document.querySelector('.graphs-bar').offsetWidth;

					bars_add.style.right = '' + (max_width_temp - bars_x - this.getBoundingClientRect().width / 2) +'px';
					bars_add.style.transform = 'translateX(50%)';

				} else {
					bar_info.classList.remove('left768px');
					bar_info.classList.remove('right768px');
					bars_add.style.left = '50%';

					bars_add.style.transform = 'translateX(-50%)';
				}

				bar_info.style.bottom = '' + String(bars_y-(bars_y_offset/2)) + 'px';

			} else {
				bars_x = this.offsetLeft + (this.getBoundingClientRect().width / 2);
				bar_info.style.left = '' + bars_x +'px';
				bar_info.style.bottom = '' + String(bars_y-(bars_y_offset/2)) + 'px';

			}*/

			bars_x = this.offsetLeft + (this.getBoundingClientRect().width / 2);
			bar_info.style.left = '' + bars_x +'px';
			bar_info.style.bottom = '' + String(bars_y-(bars_y_offset/2)) + 'px';

			bar_info.classList.add('showed');
		});

		bars_profit[i].addEventListener('mouseleave', function() {
			bar_info.classList.remove('showed');
		});



		bars_revenue[i].addEventListener('mouseover', function() {

			result = [];
			result.push(this.getAttribute('data-date_from'));
			result.push(this.getAttribute('data-date_to'));
			result.push(this.getAttribute('data-week_num'));
			result.push(this.getAttribute('data-revenue'));
			result.push(this.getAttribute('data-sales_amount'));
			result.push(this.getAttribute('data-returns_amount'));
			result.push(this.getAttribute('data-logistics'));
			result.push(this.getAttribute('data-net_costs_sum'));
			result.push(this.getAttribute('data-marginality'));
			result.push(this.getAttribute('data-commission'));
			result.push(this.getAttribute('data-supplier_costs'));
			result.push(this.getAttribute('data-wb_costs'));
			result.push(this.getAttribute('data-tax'));
			result.push(this.getAttribute('data-profit'));
			result.push(this.getAttribute('data-profitability'));

			bars_info_title.textContent = result[0] + ' - ' + result[1];

			bars_info_span[0].textContent = result[13];
			bars_info_span[1].textContent = result[8] + ' %';
			bars_info_span[2].textContent = result[14] + ' %';
			bars_info_span[3].textContent = result[4];
			bars_info_span[4].textContent = result[5];
			bars_info_span[5].textContent = result[3];
			bars_info_span[6].textContent = result[7];
			bars_info_span[7].textContent = result[9];
			bars_info_span[8].textContent = result[6];
			bars_info_span[9].textContent = result[11];
			bars_info_span[10].textContent = result[10];
			bars_info_span[11].textContent = result[12];


			/*if (screen_width <= 480) {
				bar_info.style.bottom = '' + String(-1*(bars_y-(bars_y_offset/2)) +10) + 'px';

				bars_x = this.offsetLeft + (this.getBoundingClientRect().width / 2);

				bars_add.style.left = '' + bars_x +'px';


			} else if (screen_width <= 768) {

				bars_x = this.offsetLeft + (this.getBoundingClientRect().width / 2);
				bar_info.style.left = '' + bars_x +'px';

				position = this.getAttribute('data-position');
				if (position == 'left') {
					bar_info.style.left = 0;

					bar_info.classList.add('left768px');
					bars_add.style.left = '' + bars_x +'px';

					bars_add.style.transform = 'translateX(-50%)';

				} else if (position == 'right') {
					bar_info.style.left = 'auto';
					bar_info.style.right = '0';

					bar_info.classList.add('right768px');
					bars_add.style.left = 'auto';


					bars_x = this.offsetLeft;

					max_width_temp = document.querySelector('.graphs-bar').offsetWidth;

					bars_add.style.right = '' + (max_width_temp - bars_x - this.getBoundingClientRect().width / 2) +'px';
					bars_add.style.transform = 'translateX(50%)';

				} else {
					bar_info.classList.remove('left768px');
					bar_info.classList.remove('right768px');
					bars_add.style.left = '50%';

					bars_add.style.transform = 'translateX(-50%)';
				}

				bar_info.style.bottom = '' + String(bars_y-(bars_y_offset/2)) + 'px';

			} else {
				bars_x = this.offsetLeft + (this.getBoundingClientRect().width / 2);
				bar_info.style.left = '' + bars_x +'px';
				bar_info.style.bottom = '' + String(bars_y-(bars_y_offset/2)) + 'px';

			}*/

			bars_x = this.offsetLeft + (this.getBoundingClientRect().width / 2);
			bar_info.style.left = '' + bars_x +'px';
			bar_info.style.bottom = '' + String(bars_y-(bars_y_offset/2)) + 'px';

			bar_info.classList.add('showed');



			/*if (screen_width <= 480) {
				bar_info.style.bottom = '' + String(-1*(bars_y-(bars_y_offset/2)) +10) + 'px';

				bars_x = this.offsetLeft + (this.getBoundingClientRect().width / 2);
				bars_add.style.left = '' + bars_x +'px';


			} else if (screen_width <= 768) {

			} else {
				bars_x = this.offsetLeft + (this.getBoundingClientRect().width / 2);
				bar_info.style.left = '' + bars_x +'px';
				bar_info.style.bottom = '' + String(bars_y-(bars_y_offset/2)) + 'px';

			}

			bar_info.classList.add('showed');*/

		});

		bars_revenue[i].addEventListener('mouseleave', function() {
			bar_info.classList.remove('showed');
		});
	}

}

var diog_current_title = '';

function createDiogram(data, position) {

	let data_original = data;

	let cur_block = 'diog-' + position;

	let diog_content = document.getElementById(cur_block);

	let diog_labeles = [];
	let diog_data = [];

	let count_key = 0;
	for (key in data) {
		diog_labeles.push(key.toUpperCase());
		diog_data.push(data[key]);

		count_key = count_key + 1;
	}
	let diog_legend_block = 'graphs-diog__legend-' + position;
	diog_legend_block = document.getElementById(diog_legend_block).children;

	for(var i = 0; i < diog_labeles.length; i++) {
		diog_legend_block[i].children[1].textContent = diog_labeles[i];
	}

	let colors = [
		'#ff562b',
		'#ff815c',
		'#ffa78b',
		'#ffcabc',
		'#edecec',
		'#dfe5e9',
		'#d6dde6',
		'#b9cee2',
		'#c1d2e3',
	];
	if (count_key < 9) {
		colors = colors.slice(0, count_key);
	}
	let spans = diog_content.parentElement.parentElement.children[1].children;
	for (let i = 0; i < 9; i++) {
		if (i >= diog_data.length) {
			spans[i].classList.add('hidden');
		}
	}
	new Chart(diog_content, {
		type: 'doughnut',
		data: {
			labels: diog_labeles,
			datasets: [{
				label: '',
				data: diog_data,
				backgroundColor: colors,
			}
			]},
		options: {
			plugins: {
				legend: {
					display: false
				},
				tooltip: {
					mode: 'nearest',
					caretSize: 0,
					callbacks: {
						title : () => null,
						label: function(tooltipItem) {
							return diog_labeles[tooltipItem.dataIndex];
						},
					},
					bodyFont: {
						size: 8
					},
					titleColor: '#0066ff',
					displayColors: false,
					backgroundColor: '#424242',
				}
			},
		}
	});
}

createBar(reportByWeekData);

createDiogram(brandShareInRevenueData, 'left');
createDiogram(stockShareInRevenueData, 'right');

graphWrapper.removeAttribute("data-report")
graphDiogWrapper.removeAttribute("data-brands-share")
graphDiogWrapper.removeAttribute("data-stock-share")


const ctx1 = document.getElementById('abc');
const abcItems = document.querySelectorAll('.abc__info-item')

let labelsABC = [];
let revenuesData = [];
let shareInRevenuesData = [];

abcItems.forEach(item => {
	labelsABC.push(item.getAttribute('data-abc-group'))
	revenuesData.push(item.getAttribute('data-abc-revenue'))
	shareInRevenuesData.push(item.getAttribute('data-abc-share'))
})

new Chart(ctx1, {
	type: 'bar',
	data: {
		labels: labelsABC,
		datasets: [{
			data: revenuesData,
			backgroundColor: ["#ff8364", "#dbdbdb", "#c0cee0"],
			borderWidth: 0,
			borderRadius: 10,
			categoryPercentage: 0.8,
			barPercentage: 1.0,
			order: 1,
			yAxisID: "bar_data"
		},
			{
				data: shareInRevenuesData,
				borderColor: "#424242",
				backgroundColor: "#424242",
				type: 'line',
				order: 0,
				yAxisID: "linear_data"
			}]
	},
	options: {
		responsive: true,
		plugins: {
			legend: {
				display: false,
			},
			tooltip: {
				enabled: false
			}
		},
		scales: {
			bar_data: {
				beginAtZero: true,
				type: 'linear',
				position: 'left',
				grid: {
					display: false
				},
				ticks: {
					display: false
				},
				border: {
					display: false
				},
			},
			linear_data: {
				beginAtZero: true,
				type: 'linear',
				position: 'right',
				grid: {
					display: false
				},
				ticks: {
					display: false
				},
				border: {
					display: false
				},
			},
			x: {
				ticks: {
					font: {
						size: 8,
					}
				},
				grid: {
					display: false
				},
				border: {
					color: "#dbdbdb",
					width: 2
				},

			},
			y: {
				ticks: {
					display: false
				},
				border: {
					display: false
				},
				grid: {
					display: false,
				}
			},
		}
	}
});