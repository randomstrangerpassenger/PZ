-- Supported detail-model facade. Assembly and engine access have dedicated owners.
local Assembler = require("Iris/UI/Detail/IrisItemDetailModelAssembler")

local ViewModel = {}

ViewModel.copyArray = Assembler.copyArray
ViewModel.arrayLength = Assembler.arrayLength
ViewModel.isViewModel = Assembler.isViewModel
ViewModel.fromItem = Assembler.fromItem
ViewModel.ensure = Assembler.ensure
ViewModel.getInstrumentation = Assembler.getInstrumentation
ViewModel.resetInstrumentation = Assembler.resetInstrumentation
ViewModel.setInstrumentationEnabled = Assembler.setInstrumentationEnabled

return ViewModel
