// Copyright (C) 2020 Intel Corporation
//
// SPDX-License-Identifier: MIT

import React from 'react';
import { connect } from 'react-redux';

import {
    TasksQuery,
    CombinedState,
    ActiveInference,
} from 'reducers/interfaces';

import TaskItemComponent from 'components/tasks-page/task-item';

import { getTasksAsync } from 'actions/tasks-actions';
import { cancelInferenceAsync } from 'actions/models-actions';

interface StateToProps {
    deleted: boolean;
    hidden: boolean;
    previewImage: string;
    taskInstance: any;
    activeInference: ActiveInference | null;
    user: any;
}

interface DispatchToProps {
    getTasks(query: TasksQuery): void;
    cancelAutoAnnotation(): void;
}

interface OwnProps {
    idx: number;
    taskID: number;
}

function mapStateToProps(state: CombinedState, own: OwnProps): StateToProps {
    const task = state.tasks.current[own.idx];
    const { deletes } = state.tasks.activities;
    const id = own.taskID;
    const { auth } = state

    return {
        hidden: state.tasks.hideEmpty && task.instance.jobs.length === 0,
        deleted: id in deletes ? deletes[id] === true : false,
        previewImage: task.preview,
        taskInstance: task.instance,
        activeInference: state.models.inferences[id] || null,
        user: auth.user,
    };
}

function mapDispatchToProps(dispatch: any, own: OwnProps): DispatchToProps {
    return {
        getTasks(query: TasksQuery): void {
            dispatch(getTasksAsync(query));
        },
        cancelAutoAnnotation(): void {
            dispatch(cancelInferenceAsync(own.taskID));
        },
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(TaskItemComponent);
