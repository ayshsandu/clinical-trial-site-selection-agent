import jwt from 'jsonwebtoken';
import { Request } from 'express';

export function logRequestDetails(req: Request) {
  const authHeader = req.headers['authorization'];
  if (authHeader && authHeader.startsWith('Bearer ')) {
    const token = authHeader.substring(7);
    try {
      const decoded = jwt.decode(token) as any;
      const sub = decoded?.sub;
      const act = decoded?.act?.sub;
      const toolName = req.body?.params?.name;
      const args = req.body?.params?.arguments;
      console.log(`REQUESTED TOOL: ${toolName}, Sub: ${sub}, Act: ${act}, AND ARGS ${JSON.stringify(args)}`);
    } catch (error) {
      console.error('Error decoding JWT:', error);
    }
  }
}