# HANDOFF

owner：独立验收任务 01a0c5b4-bd94-7110-94a8-5b2c9e190508。
协调：01a0c3c3-e4c7-7b71-be7e-110ef965a333。
PM：01a0c5b4-a19c-7810-8c6e-d8a87bb68f70；测试：01a0c5b4-aff1-7102-85c2-bb1a66b8368f。

当前：产品e948b2c5edc28ca34301903b3066f07119a379ee的G1 PASS，验收提交4a6c78f028df8075504ac5ebd028d5f392dede03已push供协调整合。三版完整EDC与Demo NO-GO；独立附件几何修复复测进行中。不得合并main；只由协调整合。后续修复必须列被审SHA，不将旧版结论套新版。模型README旧交互映射不作为固件权威，新产品目录优先。

最终更新：测试ad0c363bdaeb95702185c0f9bc3ce14204ad161e已审，三修复模型仅限定G2有条件通过；完整SHA/关闭问题/余留阻塞见REVIEW末节。本轮独立文档评审任务完成，G3/G4与价值验证未完成是产品实证阻塞，不是文档未交付。后续收到合法源测量、试制、固件与现场演练证据后再开启对应门复审。最终验收提交通过任务消息交总控；不自动清理worktree。

最新产品68dbb10bd414d80be85657f497de9e390434d8c3事实同步已增量审查，G1 PASS对应此最终SHA；e948b2c为此前完整协议审查记录。

新一轮：codex/original-acceptance，最新范围以ORIGINAL_CRITERIA.md为准，进展ORIGINAL_REVIEW.md。软件任务01a0c5c6-3e14-7e80-b9c0-3e7159c57977。旧原玩具缺尺寸不再是原创阻塞；O1/O2可独立交付，O3/O4需实机/实打证据。只改本目录，不写模型/APP，不合main。

0daf340补充验收：见ORIGINAL_REVIEW及state-probe；O2仍有状态/保存/模式问题，O3未测且协议阻断。后续按修复SHA运行state-probe/run.ps1；若生产接口变化需显式调整stub并保留原结果，不覆盖历史失败证据。

最终机械矩阵已锁独测00d5e76；三款O1 PASS、O4 NOT_TESTED，详见ORIGINAL_MODEL_MATRIX。软件锁a5b99b0/34BB，只关闭15条Java状态/ACK/U10数据反例；等待同包独测与PM最终视觉，不接旧包结论。
