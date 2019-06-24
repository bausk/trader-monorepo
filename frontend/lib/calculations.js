import Moment from 'moment';

export class DataTransformations {
    constructor(dataset) {
        this.dataset = dataset;
        this.result = null;
        this.startDate = Moment();
        this.endDate = Moment();
    }

    getLatestDate = () => {
        this.result = this.dataset[this.dataset.length - 1];
        this.startDate = Moment.unix(this.result.DateTime / 1000);
        this.endDate = Moment.unix(this.result.DateTime / 1000);
        return this;
    }

    getClosestDate = (date) => {
        for (const [i, daySlice] of this.dataset.entries()) {
            const dayDateTime = Moment.unix(daySlice.DateTime / 1000);
            if (date <= dayDateTime) {
                return [dayDateTime, daySlice, i];
            }
        }
        const daySlice = this.dataset[this.dataset.length - 1];
        return [Moment.unix(daySlice.DateTime / 1000), daySlice, this.dataset.length - 1];
    }

    getDatasetClosestToDate = (date) => {
        const res = this.getClosestDate(date);
        this.result = res[1];
        this.startDate = res[0];
        this.endDate = res[0];
        return this;
    };

    getDatasetsInRange = (startDate, endDate) => {
        const startValues = this.getClosestDate(startDate);
        const endValues = this.getClosestDate(endDate);
        this.result =  this.dataset.slice(startValues[2], endValues[2] + 1);
        this.startDate = startValues[0];
        this.endDate = endValues[0];
        return this;
    };

    singleDayToSurface = (series, factor) => {
        const rX = [];
        const rY = [];
        const rZ = [];
        const cellA = 24;
        const cellB = (6 * 3) + (4.5 * 2);
        let x_offset = 0;
        let y_offset = 0;
        const walk = (o1, o2) => ({ o1: o1, o2: o2 + cellB });
        [
            [series.X1, series.Y1],
            [series.X2, series.Y2],
            [series.X3, series.Y3],
            [series.X4, series.Y4]
        ].forEach((incls) => {
            const inclX = incls[0];
            const inclY = incls[1];
            let X = x_offset;
            let Y = y_offset;
            let Z = (inclX * (cellB / 2) + inclY * (cellA / 2)) / 1000;
            rX.push(X);
            rY.push(Y);
            rZ.push(Z);

            X = x_offset + cellA;
            Y = y_offset;
            Z = (inclX * (cellB / 2) - inclY * (cellA / 2)) / 1000;
            rX.push(X);
            rY.push(Y);
            rZ.push(Z);

            X = x_offset;
            Y = y_offset + cellB;
            Z = (-inclX * (cellB / 2) + inclY * (cellA / 2)) / 1000;
            rX.push(X);
            rY.push(Y);
            rZ.push(Z);

            X = x_offset + cellA;
            Y = y_offset + cellB;
            Z = (-inclX * (cellB / 2) - inclY * (cellA / 2)) / 1000;
            rX.push(X);
            rY.push(Y);
            rZ.push(Z);

            const { o1, o2 } = walk(x_offset, y_offset);
            x_offset = o1;
            y_offset = o2;
        });
        return [rX, rY, rZ.map(z => (z * factor)), rZ];
    }

    resultToSurfaces = (factor = 1) => {
        if (this.result.length) {
            return this.result.map((r) => this.singleDayToSurface(r, factor));
        }
        return this.singleDayToSurface(this.result, factor);
    }

}