```
 } else if (rawLen == 14) {
                // 新的14位二维码格式: 版本号(1位) + 设备类型(1位) + MAC地址(12位)
                // 例如: 2P0a0c11223834
                if (mWhichTo != null && !TextUtils.isEmpty(mWhichTo)) {
                    try {
                        when (result[0]) {
                            '2' -> {
                                val deviceType = result[1] // P = POS机
                                val mac = result.substring(2, 14)
                                if (deviceType == 'P' && mac.matches(Regex("[0-9a-fA-F]{12}"))) {
                                    val curType = "CloudPos-V1"

                                    val extras = Bundle()
                                    extras.putString(INTENT_TAG_MAC, mac)  // 直接使用原始MAC，不格式化
                                    extras.putString(INTENT_TAG_TYPE, curType)
                                    extras.putString(SCAN_INTENT_TAG_TO, mWhichTo)
                                    extras.putString(INTENT_ROOT_ID_TAG, mRootId)
                                    readyGo(DeviceEnterModeActivity::class.java, extras)
                                }
                                else {
                                    KLog.e(TAG, "14位二维码MAC地址格式错误: $mac 或当前type不为Pos机: $deviceType")
                                }
                            }
                            else -> {

                            }
                        }
                    } catch (e: Exception) {
                        KLog.e(TAG, "14位二维码解析失败: $result", e)
                        ToastUtil.showToast(this, "二维码格式错误：解析失败")
                    }
                } else {
                    mCommonDialog = CommonDialog(this, CommonDialog.DlgStyle.TWO_BTN, getString(R.string.app_name), getString(R.string.str_dialog_capture_message), object : CommonDialog.OnDlgClkListener {
                        override fun onDlgPositiveBtnClk() {
                            // 显示扫描框，并开始识别
                            mZXingView?.startSpotAndShowRect()
                        }

                        override fun onDlgOneBtnClk() {}
                        override fun onDlgNegativeBtnClk() {
                            finish()
                        }

                        override fun onCancel() {
//                            if (handler != null) {
//                                handler!!.sendEmptyMessage(R.id.restart_preview)
//                            }
                        }
                    })
                    mCommonDialog!!.show()
                }
            } else if (result?.startsWith("@#$%") == true && result.endsWith("@#$%")) {
```

