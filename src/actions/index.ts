import { Action } from '../types';

const actions: Action[] = [
  {
    command: '!coffeemoney',
    description: 'hello world!',
    fn: (args) => `My args are ${args}`,
  },
];

function parseArgs(command: string): [cmd: string, args: string[]] {
  const strArr = command.split(' ');
  return [strArr[0], strArr.slice(1, strArr.length)];
}

type ActionExecution = string | null;

export function executeAction(command: string): ActionExecution {
  const [cmd, args] = parseArgs(command);
  const action = actions.find((action) => action.command === cmd);
  if (action) {
    return action.fn(args);
  }

  return null;
}
