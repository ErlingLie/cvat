// Copyright (C) 2020 Intel Corporation
//
// SPDX-License-Identifier: MIT

import React from 'react';
import { RouteComponentProps } from 'react-router';
import { withRouter } from 'react-router-dom';
import { Row, Col } from 'antd/lib/grid';
import Button from 'antd/lib/button';
import Input from 'antd/lib/input';
import Text from 'antd/lib/typography/Text';

interface VisibleTopBarProps {
    onSearch: (value: string) => void;
    searchValue: string;
    user: any;
    numberOfCompletedTasks: number;
}

function TopBarComponent(props: VisibleTopBarProps & RouteComponentProps): JSX.Element {
    const {
        searchValue,
        history,
        onSearch,
        user,
        numberOfCompletedTasks,
    } = props;

    const is_superuser = user == null ? false : user.isSuperuser
    let str_text = "Number of annotated segments: " + numberOfCompletedTasks.toString(10);
    return (
        <>
            <Row type='flex' justify='center' align='middle'>
                <Col md={22} lg={18} xl={16} xxl={14}>
                    <Text strong>Default project</Text>
                </Col>
            </Row>
            <Row type='flex' justify='center' align='middle'>
                <Col md={11} lg={9} xl={8} xxl={7}>
                    <Text className='cvat-title'>Tasks</Text>
                    <Input.Search
                        defaultValue={searchValue}
                        onSearch={onSearch}
                        size='large'
                        placeholder='Search'
                    />
                </Col>
                <Col
                    md={{ span: 11 }}
                    lg={{ span: 9 }}
                    xl={{ span: 8 }}
                    xxl={{ span: 7 }}
                >
                    {is_superuser &&
                    <Button
                        size='large'
                        id='cvat-create-task-button'
                        type='primary'
                        onClick={
                            (): void => history.push('/tasks/create')
                        }
                        icon='plus'
                    >
                         Create new task
                    </Button> }
                    {!is_superuser &&
                        <Text strong>{str_text}</Text>
                        }
                </Col>
            </Row>
        </>
    );
}

export default withRouter(TopBarComponent);
