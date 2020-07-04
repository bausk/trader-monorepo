import React, { useRef, useState, useEffect } from 'react';
import { useDebouncedCallback } from 'use-debounce';
import { createChart } from 'lightweight-charts';
import { DateTime } from "luxon";


const LightweightChart = ({ dataType, newData, newAutorefreshData, onRangeChanged, period }) => {
    const canvasRoot = useRef(null);
    const primarySeries = useRef(null);
    const [ isFirstInit, setIsFirstInit ] = useState(true);
    const chr = useRef(null);
    const [ onChanged ] = useDebouncedCallback(() => {
        const logicalRange = chr.current.timeScale().getVisibleLogicalRange();
        const barsInfo = primarySeries.current.barsInLogicalRange(logicalRange);
        if (barsInfo !== null && barsInfo.barsBefore < 50) {
            const visibleRange = chr.current.timeScale().getVisibleRange();
            const barsToLoad = 100 - barsInfo.barsBefore;
            const startTime = DateTime.fromSeconds(visibleRange.from).minus({ minutes: barsToLoad * period });
            const endTime = DateTime.fromSeconds(visibleRange.from).plus({ minutes: 10 * period })
            onRangeChanged({
                from: startTime,
                to: endTime
            });
        }
    }, 1000);
    useEffect(() => {
        const chart = createChart(
            canvasRoot.current,
            { width: 800, height: 400 }
        );
        chr.current = chart;
        chr.current.applyOptions({
            layout: {
                backgroundColor: '#F0F0F1',
                textColor: '#696969',
                fontSize: 14,
                fontFamily: 'Calibri',
            },
        });
        let series;
        if (dataType === 'candlestick') {
            series = chart.addCandlestickSeries();
        } else {
            series = chart.addLineSeries();
        }
        primarySeries.current = series;
        // TODO: add are, document, or remove
        // const areaSeries = inputEl.current.addAreaSeries({
        //     topColor: 'rgba(21, 146, 230, 0.4)',
        //     bottomColor: 'rgba(21, 146, 230, 0)',
        //     lineColor: 'rgba(200, 100, 100, 1)',
        //     lineStyle: 0,
        //     lineWidth: 6,
        //     crosshairMarkerVisible: false,
        //     crosshairMarkerRadius: 0,
        // });
        // areaSeries.setData([
        //     { time: Date.parse('2019-04-13 02:01:00')/1000, value: 120.01 },
        //     { time: Date.parse('2019-04-13 02:03:00')/1000, value: 120.01 },
        // ]);
        // const candlestickSeries = inputEl.current.addCandlestickSeries();
        // candlestickSeries.setData([
        //     { time: Date.parse("2019-04-13 02:01:00")/1000, open: 141.77, high: 170.39, low: 120.25, close: 145.72 },
        //     { time: Date.parse("2019-04-13 02:02:00")/1000, open: 145.72, high: 147.99, low: 100.11, close: 108.19 },
        //     { time: Date.parse("2019-04-13 02:03:00")/1000, open: 108.19, high: 118.43, low: 74.22, close: 75.16 },
        //     { time: Date.parse("2019-04-13 02:04:00")/1000, open: 75.16, high: 82.84, low: 36.16, close: 45.72 },
        //     { time: Date.parse("2019-04-13 02:05:00")/1000, open: 45.12, high: 53.90, low: 45.12, close: 48.09 },
        //     { time: Date.parse("2019-04-13 02:06:00")/1000, open: 60.71, high: 60.71, low: 53.39, close: 59.29 },
        //     { time: Date.parse("2019-04-13 02:07:00")/1000, open: 68.26, high: 68.26, low: 59.04, close: 60.50 },
        //     { time: Date.parse("2019-04-13 02:08:00")/1000, open: 67.71, high: 105.85, low: 66.67, close: 91.04 },
        //     { time: Date.parse("2019-04-13 02:09:00")/1000, open: 91.04, high: 121.40, low: 82.70, close: 111.40 },
        //     { time: Date.parse("2019-04-13 02:10:00")/1000, open: 111.51, high: 142.83, low: 103.34, close: 131.25 },
        //     { time: Date.parse("2019-04-13 02:11:00")/1000, open: 131.33, high: 151.17, low: 77.68, close: 96.43 },
        //     { time: Date.parse("2019-04-13 02:12:00")/1000, open: 106.33, high: 110.20, low: 90.39, close: 98.10 },
        //     { time: Date.parse("2019-04-13 02:13:00")/1000, open: 109.87, high: 114.69, low: 85.66, close: 111.26 },
        // ]);
        chr.current.timeScale().subscribeVisibleTimeRangeChange(onChanged);

        return () => {
            chr.current.timeScale().unsubscribeVisibleTimeRangeChange(onChanged);
        }
    }, []);

    const tickToChart = (tick) => {
        return { time: Date.parse(tick.queried_at)/1000, value: tick.price };
    };

    const ohlcToChart = (ohlc) => {
        return {
            time: Date.parse(ohlc.time)/1000,
            open: ohlc.open,
            high: ohlc.high,
            low: ohlc.low,
            close: ohlc.close,
            volume: ohlc.volume,
        };
    };

    useEffect(() => {
        if (newData?.length) {
            const parsed = (dataType === 'candlestick') ?
                newData.map(ohlcToChart) :
                newData.map(tickToChart);
            if (isFirstInit) {
                primarySeries.current.setData(parsed);
                chr.current.applyOptions({
                    timeScale: {
                        rightOffset: 12,
                        barSpacing: 3,
                        //lockVisibleTimeRangeOnResize: true,
                        //rightBarStaysOnScroll: true,
                        borderVisible: false,
                        borderColor: '#fff000',
                        visible: true,
                        timeVisible: true,
                        secondsVisible: true,
                        fixLeftEdge: true,
                    },
                });
                setIsFirstInit(false);
            } else {
                parsed.map(b => primarySeries.current.update(b));
            }
        }
    }, [newData, dataType]);

    useEffect(() => {
        if (newAutorefreshData?.length) {
            const parsed = (dataType === 'candlestick') ?
                newData.map(ohlcToChart) :
                newData.map(tickToChart);
            parsed.map(b => primarySeries.current.update(b));
        }
    }, [newAutorefreshData, dataType]);



    return (
        <>
            <div ref={canvasRoot} />
        </>
    );
};

export default LightweightChart;