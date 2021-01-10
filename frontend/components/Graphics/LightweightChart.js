import React, { useRef, useState, useEffect, useCallback } from 'react';
import { useDebouncedCallback } from 'use-debounce';
import { createChart } from 'lightweight-charts';
import { DateTime } from "luxon";


const LightweightChart = ({ dataType, markers, newData, newAutorefreshData, onRangeChanged, period }) => {
    const canvasRoot = useRef(null);
    const primarySeries = useRef(null);
    const secondarySeries = useRef(null);
    const upperPrimitive = useRef(null);
    const lowerPrimitive = useRef(null);
    const mainIndicator = useRef(null);
    const [ isFirstInit, setIsFirstInit ] = useState(true);
    const [ isFirstSecInit, setIsFirstSecInit ] = useState(true);
    const chr = useRef(null);

    // Reacts to visible range change events
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

    const [ selectedMarker, setSelectedMarker ] = useState(null);
    const [ selectedPrice, setSelectedPrice ] = useState(null);
    const onMarkerClick = useCallback((param) => {
        if (param.hoveredMarkerId) {
            const price = param.seriesPrices.values().next().value.close;
            setSelectedMarker(param.hoveredMarkerId);
            setSelectedPrice(price);
        }
    }, []);

    const timeseriesToChart = useCallback((timeseries) => {
        const amplifier = selectedPrice * 0.1;
        return { time: Date.parse(timeseries.timestamp)/1000, value: (timeseries.value * amplifier + selectedPrice) };
    }, [selectedPrice]);

    const primitivesToMainIndicator = useCallback((primitives) => {
        const buy = primitives[0];
        const sell = primitives[1];
        const hash = buy.reduce((acc, ts) => {
            const time = Date.parse(ts.timestamp)/1000;
            const color = ts.value > 0 ? 'rgba(105, 189, 231, 0.7)' : 'rgba(0, 0, 0, 0.2)';
            acc[time] = { time, value: ts.value, color };
            return acc;
        }, {});
        sell.forEach((ts) => {
            const time = Date.parse(ts.timestamp)/1000;
            const old = hash[time];
            const color = ts.value < 0 ? 'rgba(245, 161, 67, 0.86)' : 'rgba(0, 0, 0, 0.2)';
            if (!old || old.value <= Math.abs(ts.value)) {
                hash[time] = { time, value: -ts.value, color };
            }
        });
        return Object.values(hash);
    }, []);

    // Draw primitives each time selected marker changes
    useEffect(() => {
        if (markers && selectedMarker) {
            const selectedMarkerData = markers[selectedMarker];
            const upperData = selectedMarkerData.primitives[0]?.map(timeseriesToChart);
            const lowerData = selectedMarkerData.primitives[1]?.map(timeseriesToChart);
            upperPrimitive.current.setData(upperData);
            lowerPrimitive.current.setData(lowerData);
        }
    }, [selectedMarker, markers, timeseriesToChart]);


    // Calculate and draw volumes each time selected marker changes
    useEffect(() => {
        if (markers && selectedMarker) {
            const selectedMarkerData = markers[selectedMarker];
            const mainIndicatorData = primitivesToMainIndicator(selectedMarkerData.primitives);
            mainIndicator.current.setData(mainIndicatorData);
        }
    }, [selectedMarker, markers, primitivesToMainIndicator]);
    
    // Runs once on chart initialization, does not put data on chart
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
        let secondary;
        if (dataType === 'candlestick') {
            series = chart.addCandlestickSeries({
                priceScaleId: 'right',
                scaleMargins: {
                    top: 0.0,
                    bottom: 0.3,
                },
            });
            secondary = chart.addLineSeries({
                priceScaleId: 'right'
            });
        } else {
            series = chart.addLineSeries({
                priceScaleId: 'right'
            });
        }
        primarySeries.current = series;
        secondarySeries.current = secondary;
        upperPrimitive.current = chart.addLineSeries({
            lineColor: 'rgba(10, 180, 0, 0.6)',
            lineStyle: 0,
            lineWidth: 2,
            priceScaleId: 'left',
        });
        lowerPrimitive.current = chart.addLineSeries({
            lineColor: 'rgba(160, 0, 0, 0.6)',
            сolor: 'rgba(160, 0, 0, 0.6)',
            lineStyle: 0,
            lineWidth: 1,
            priceScaleId: 'left',
        });
        mainIndicator.current = chart.addHistogramSeries({
            color: '#26a69a',
            lineWidth: 1,
            priceFormat: {
                type: 'volume',
            },
            overlay: true,
            scaleMargins: {
                top: 0.7,
                bottom: 0.0,
            },
        });
        chr.current.timeScale().subscribeVisibleTimeRangeChange(onChanged);
        chr.current.subscribeClick(onMarkerClick);
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

    // Reacts to arrival of new data on chart scroll.
    // New data is cumulative, all further updates
    // add up and nothing is deleted.
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

    // Reacts to new recent-most data which are polled at an interval.
    // Cumulative update, nothing is deleted.
    // TODO: Fix this, it's currently broken for unknown reason.
    useEffect(() => {
        if (newAutorefreshData?.length) {
            const parsed = (dataType === 'candlestick') ?
                newData.map(ohlcToChart) :
                newData.map(tickToChart);
            parsed.map(b => primarySeries.current.update(b));
        }
    }, [newAutorefreshData, dataType]);

    // Reacts to changed markers. Not cumulative.
    useEffect(() => {
        const series = primarySeries.current;
        const positions = {
            BUY_ALL: 'belowBar',
            SELL_ALL: 'belowBar',
            AMBIGUOUS: 'belowBar',
            NO_DATA: 'belowBar'
        };
        const shapes = {
            BUY_ALL: 'arrowUp',
            SELL_ALL: 'arrowDown',
            AMBIGUOUS: 'circle',
            NO_DATA: 'circle'
        };
        const colors = {
            BUY_ALL: 'green',
            SELL_ALL: 'red',
            AMBIGUOUS: '#546e7aaa',
            NO_DATA: 'grey'
        };
        const sizes = {
            BUY_ALL: 1,
            SELL_ALL: 1,
            AMBIGUOUS: 0.2,
            NO_DATA: 1
        };
        const preparedMarkers = markers && Object.entries(markers).map(([ time, marker ]) => {
            const direction = marker.direction;
            return { 
                time: parseInt(time),
                id: time,
                position: positions[direction],
                color: colors[direction],
                shape: shapes[direction],
                size: sizes[direction],
            };
        });
        preparedMarkers && series?.setMarkers(preparedMarkers);
    }, [markers, primarySeries, chr]);


    return (
        <>
            <div ref={canvasRoot} />
        </>
    );
};

export default LightweightChart;